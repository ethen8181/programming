import scala.math
import spark.implicits._
import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.ml.linalg.{Vector, Vectors}
import org.apache.spark.ml.{Pipeline, PipelineModel}
import org.apache.spark.ml.clustering.{KMeans, KMeansModel}
import org.apache.spark.ml.feature.{OneHotEncoder, StringIndexer}
import org.apache.spark.ml.feature.{VectorAssembler, StandardScaler}
import scala.util.Random


val spark = SparkSession.builder().getOrCreate()
val basepath = "/Users/ethen/programming/advanced_analytics_spark/ch05-kmeans/"
val data = spark.read.
    option("inferSchema", true).
    option("header", false).
    csv(basepath + "kddcup.data").
    toDF("duration", "protocol_type", "service", "flag",
         "src_bytes", "dst_bytes", "land", "wrong_fragment", "urgent",
         "hot", "num_failed_logins", "logged_in", "num_compromised",
         "root_shell", "su_attempted", "num_root", "num_file_creations",
         "num_shells", "num_access_files", "num_outbound_cmds",
         "is_host_login", "is_guest_login", "count", "srv_count",
         "serror_rate", "srv_serror_rate", "rerror_rate", "srv_rerror_rate",
         "same_srv_rate", "diff_srv_rate", "srv_diff_host_rate",
         "dst_host_count", "dst_host_srv_count",
         "dst_host_same_srv_rate", "dst_host_diff_srv_rate",
         "dst_host_same_src_port_rate", "dst_host_srv_diff_host_rate",
         "dst_host_serror_rate", "dst_host_srv_serror_rate",
         "dst_host_rerror_rate", "dst_host_srv_rerror_rate", "label").
    sample(false, 0.1)

data.cache()


// fit a single pipeline, print out cluster centers and compute SSE
// val assembleCols = (Set(data.columns: _*) -- 
//     Seq("label", "protocol_type", "service", "flag"))
// val assembler = new VectorAssembler().
//     setInputCols(assembleCols.toArray).
//     setOutputCol("featureVector")
// val kmeans = new KMeans().
//     setK(2).
//     setPredictionCol("cluster").
//     setFeaturesCol(assembler.getOutputCol)
// val pipeline = new Pipeline().setStages(Array(assembler, kmeans))
// val pipelineModel = pipeline.fit(data)

// val kmeansModel = pipelineModel.stages.last.asInstanceOf[KMeansModel]
// kmeansModel.clusterCenters
// val score = kmeansModel.computeCost(assembler.transform(data)) / data.count
// println(score)


def oneHotPipeline(inputCol: String): (Pipeline, String) = {
    /*
    pipeline for one-hot encoding a single column,
    returns the Pipeline object and output vector column's name
    */
    val indexer = new StringIndexer().
        setInputCol(inputCol).
        setOutputCol(inputCol + "_indexed")
    val encoder = new OneHotEncoder().
        setInputCol(indexer.getOutputCol).
        setOutputCol(inputCol + "_vec")
    val pipeline = new Pipeline().setStages(Array(indexer, encoder))
    (pipeline, inputCol + "_vec")
}


def fitPipeline(data: DataFrame, k: Int): PipelineModel = {

    // standard one-hot encoding
    val (protoTypeEncoder, protoTypeVecCol) = oneHotPipeline("protocol_type")
    val (serviceEncoder, serviceVecCol) = oneHotPipeline("service")
    val (flagEncoder, flagVecCol) = oneHotPipeline("flag")
    
    /* 
    Original columns, without label and string columns, but 
    with new one-hot encoded string columns
    */
    val assembleCols = Set(data.columns: _*) --
        Seq("label", "protocol_type", "service", "flag") ++
        Seq(protoTypeVecCol, serviceVecCol, flagVecCol)
    
    val assembler = new VectorAssembler().
        setInputCols(assembleCols.toArray).
        setOutputCol("featureVector")

    val scaler = new StandardScaler().
        setInputCol(assembler.getOutputCol).
        setOutputCol("scaledFeatureVector").
        setWithStd(true).
        setWithMean(true)

    // useful to increase the max iter and tolerance to ensure convergence
    val kmeans = new KMeans().
        setK(k).
        setMaxIter(40).
        setTol(1.0e-5).
        setSeed(Random.nextLong()).
        setPredictionCol("cluster").
        setFeaturesCol(scaler.getOutputCol)

    val pipeline = new Pipeline().setStages(
        Array(protoTypeEncoder, serviceEncoder, flagEncoder, assembler, scaler, kmeans))
    pipeline.fit(data)
}


def clusteringScore(data: DataFrame, k: Int): Double = {
    // construct the pipeline to compute the cluster's score

    val pipelineModel = fitPipeline(data, k)
    val clusterLabel = pipelineModel.
        transform(data).
        select("cluster", "label").as[(Int, String)]

    // computes entropy of the label for each cluster group
    def entropy(counts: Iterable[Int]): Double = {
        val values = counts.filter(_ > 0)
        val n = values.map(_.toDouble).sum
        values.map { v =>
            val p = v / n
            -p * math.log(p)
        }.sum
    }

    /*
    1. groupByKey: collect the label collection for each cluster
    2. mapGroup : disregard the cluster group and perform action
    on the label collection
    3. Scala sequence groupBy identity explained:
    https://www.java-success.com/10-%E2%99%A5-coding-scala-way-groupby-mapvalues-identity/
    */
    val weightedClusterEntropy = clusterLabel.
        groupByKey { case (cluster, _) => cluster}.
        mapGroups { case (_, clusterLabels) => 
            val labels = clusterLabels.toSeq
            val labelCounts = labels.groupBy(identity).values.map(_.size)
            labels.size * entropy(labelCounts)
        }.collect
    weightedClusterEntropy.sum / data.count
}

/*
syntax for creating a collection of numbers between start to 
end (inclusive) with a fix difference between successive elements
*/
(20 to 40 by 20).
map(k => (k, clusteringScore(data, k))).
foreach(println)


/*
Fit the model that has the minimum entropy and
display the label for each cluster
to get some sense of resulting cluster, ideally
each cluster should be dominated by one type of cluster
*/
val pipelineModel = fitPipeline(data, k = 80)
val clusterLabel = pipelineModel.
    transform(data).
    select("cluster", "label").
    groupBy("cluster", "label").
    count.
    orderBy("cluster", "label").
    show

val kmeansModel = pipelineModel.stages.last.asInstanceOf[KMeansModel]
val centroids = kmeansModel.clusterCenters
val clustered = pipelineModel.transform(data)


/* 
1. Pick a threshold: i.e. for a new data point measure its distance
to the nearest centroid, and if that distance exceeds a certain user-defined
threshold, then it will be flagged as a potential anomalous point, here the
threshold is chosen to be 100-th farthest point based on known data
2. Vectors.sqdist returns a column name "value"
*/
val threshold = clustered.
    select("cluster", "scaledFeatureVector").as[(Int, Vector)].
    map { case (cluster, vec) => Vectors.sqdist(centroids(cluster), vec) }.
    orderBy($"value".desc).take(100).last

/*
Syntax for unpacking an Array to perform selecting multiple columns
https://stackoverflow.com/questions/34938770/upacking-a-list-to-select-multiple-columns-from-a-spark-data-frame/34938905
*/
val originalColumns = data.columns
val anomalies = clustered.filter { row =>
    val cluster = row.getAs[Int]("cluster")
    val feature = row.getAs[Vector]("scaledFeatureVector")
    Vectors.sqdist(centroids(cluster), feature) >= threshold
}.select(originalColumns.head, originalColumns.tail: _*)
anomalies.first()

/*
There're other more sophisticated clustering evaluation techniques
such as Silhouette coefficient and there're also other clustering algorithms
worth trying
*/
