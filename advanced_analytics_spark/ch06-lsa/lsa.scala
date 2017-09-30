import edu.umd.cloud9.collection.XMLInputFormat
import org.apache.hadoop.conf.Configuration
import org.apache.hadoop.io._
import edu.umd.cloud9.collection.wikipedia.language._
import edu.umd.cloud9.collection.wikipedia._

val basepath = "/Users/ethen/programming/advanced_analytics_spark/ch06-lsa/"
val path = basepath + "Wikipedia-20170920184300.xml"
@transient val conf = new Configuration()
conf.set(XMLInputFormat.START_TAG_KEY, "<page>")
conf.set(XMLInputFormat.END_TAG_KEY, "</page>")
val kvs = spark.sparkContext.newAPIHadoopFile(path, classOf[XMLInputFormat],
    classOf[LongWritable], classOf[Text], conf)
val rawXmls = kvs.map(_._2.toString).toDS()


def wikiXmlToPlainText(pageXml: String): Option[(String, String)] = {
    // Wikipedia has updated their dumps slightly since Cloud9 was written,
    // so this hacky replacement is sometimes required to get parsing to work.
    val hackedPageXml = pageXml.replaceFirst(
        "<text xml:space=\"preserve\" bytes=\"\\d+\">",
        "<text xml:space=\"preserve\">")

    val page = new EnglishWikipediaPage()
    WikipediaPage.readPage(page, hackedPageXml)
    if (page.isEmpty) None
    else Some((page.getTitle, page.getContent))
}

val docTexts = rawXmls.filter(_ != null).flatMap(wikiXmlToPlainText)


import scala.collection.JavaConverters._
import scala.collection.mutable.ArrayBuffer
import edu.stanford.nlp.pipeline._
import edu.stanford.nlp.ling.CoreAnnotations._
import java.util.Properties
import org.apache.spark.sql.Dataset


def createNLPPipeline(): StanfordCoreNLP = {
    val props = new Properties()
    props.put("annotators", "tokenize, ssplit, pos, lemma")
    new StanfordCoreNLP(props)
}


// broadcast the stopwords
val stopWords = scala.io.Source.fromFile(basepath + "stopwords.txt").getLines().toSet
val bStopWords = spark.sparkContext.broadcast(stopWords)


val texts = """
A visual hull is a geometric entity created by shape-from-silhouette 3D
reconstruction technique introduced by A. Laurentini. This technique assumes 
the foreground object in an image can be separated from the background.
Under this assumption, the original image can be thresholded into a foreground/background
binary image, which we call a silhouette image. The foreground mask, known as a silhouette,
is the 2D projection of the corresponding 3D foreground object. Along with the camera viewing
parameters, the silhouette defines a back-projected generalized cone that contains the actual
object. This cone is called a silhouette cone. The upper right thumbnail shows two such cones
produced from two silhouette images taken from different viewpoints. The intersection of the
two cones is called a visual hull, which is a bounding geometry of the actual 3D object (see
the bottom right thumbnail).
"""
val pipeline = createNLPPipeline()
val doc = new Annotation(texts)
pipeline.annotate(doc)

def isOnlyLetter(str: String): Boolean = {
    // .forall returns True is the expression is true for every element
    str.forall(c => Character.isLetter(c))
}


def plainTextToLemmas(text: String, stopWords: Set[String],
                      pipeline: StanfordCoreNLP): Seq[String] =  {
    val doc = new Annotation(text)
    pipeline.annotate(doc)

    val lemmas = new ArrayBuffer[String]()
    val sentences = doc.get(classOf[SentencesAnnotation]).asScala
    // Scala way of writing nested for loops
    for (sentence <- sentences;
         token <- sentence.get(classOf[TokensAnnotation]).asScala) {

        // specify some additional requirements to weed out uninformative words
        val lemma = token.get(classOf[LemmaAnnotation])
        val keep = lemma.length > 2 && !stopWords.contains(lemma) && isOnlyLetter(lemma)
        if (keep) {
            lemmas += lemma
        }
    }
    lemmas
}


/*
use mapPartitions so we only need to initialize the NLP pipeline once per chunck;
note that we can't define the object outside or else it won't be serializable
*/
val terms: Dataset[(String, Seq[String])] = docTexts.mapPartitions { iterable =>
    val pipeline = createNLPPipeline()
    iterable.map { case(title, content) =>
        val lemmas = plainTextToLemmas(content, bStopWords.value, pipeline)
        (title, lemmas)
    }
}
/*
size: Spark SQL operations that returns the length of the collection
stored in the column
http://spark.apache.org/docs/2.0.0/api/python/pyspark.sql.html
*/
val filtered = terms.
    toDF("title", "terms").
    filter(size($"terms") > 1)


import org.apache.spark.ml.feature.IDF
import org.apache.spark.ml.feature.CountVectorizer

/*
setVocabSize will leave out all but the top # of
most frequent words
*/
val numTerms = 20000
val countVectorizer = new CountVectorizer().
    setInputCol("terms").
    setOutputCol("termFreqs").
    setVocabSize(numTerms)
val vocabModel = countVectorizer.fit(filtered)
val docTermFreqs = vocabModel.transform(filtered)

// cache because it will be used at least twice (idf, document-term matrix)
docTermFreqs.cache()


val idf = new IDF().
    setInputCol(countVectorizer.getOutputCol).
    setOutputCol("tfidfVec")
val idfModel = idf.fit(docTermFreqs)
val docTermMatrix = idfModel.
    transform(docTermFreqs).
    select("title", "tfidfVec")

// mapping of index to string
val termIds: Array[String] = vocabModel.vocabulary


val docIds = docTermFreqs.
    rdd.map(_.getString(0)).
    zipWithUniqueId().
    map(_.swap).
    collect.
    toMap

import org.apache.spark.mllib.linalg.{Vectors, Vector => MLLibVector}
import org.apache.spark.ml.linalg.{Vector => MLVector}


val vecRdd = docTermMatrix.select("tfidfVec").rdd.map { row =>
    Vectors.fromML(row.getAs[MLVector]("tfidfVec"))
}


import org.apache.spark.mllib.linalg.{Matrix,
    SingularValueDecomposition}
import org.apache.spark.mllib.linalg.distributed.RowMatrix

vecRdd.cache()
val mat = new RowMatrix(vecRdd)
val k = 30
val svd = mat.computeSVD(k, computeU = true)


def topTermsInTopConcepts(
    svd: SingularValueDecomposition[RowMatrix, Matrix],
    numConcepts: Int, numTerms: Int, termIds: Array[String]) {
    // flatten the mllib Matrix to an Array, its the rows that gets flatten first
    val v = svd.V
    val arr = v.toArray

    // concatenate an array of term and its corresponding score
    val topTerms = new ArrayBuffer[Seq[(String, Double)]]()
    for (i <- 0 until numConcepts) {
        val offs = i * v.numRows
        val termWeights = arr.slice(offs, offs + v.numRows).zipWithIndex
        // negate the numeric value to sort in decreasing order
        val sorted = termWeights.sortBy(-_._1)
        topTerms += sorted.take(numTerms).map { case(score, id) =>
            (termIds(id), score)
        }
        topTerms
    }
}
val topConceptTerms = topTermsInTopConcepts(svd, 4, 10, termIds)

