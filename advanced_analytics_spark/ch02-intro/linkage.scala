val filepath = "/Users/ethen/programming/advanced_analytics_spark/ch02-intro/linkage"
val rawblocks = sc.textFile(filepath)
val head = rawblocks.take(10)

/*
it's a common functional programming pattern to process elements in a collection
using higher order functions, here we pass one function (println) as an argument
to another function (foreach) in order to perform some action.
*/
head.foreach(println)

def isHeader(line: String): Boolean = {
    // function to exclude header of array
    line.contains("id_1")
}
head.filterNot(isHeader).length

head.filter(x => !isHeader(x)).length
head.filter(isHeader(_)).length
val noheader = rawblocks.filter(x => !isHeader(x))

// DataFrame API

/*
Note that to infer the schema spark has the make two passes over the data,
thus if we know the schema that we want the file to use ahead of time,
we can create a StructType and pass it via the `schema` method
*/
val filepath = "/Users/ethen/programming/advanced_analytics_spark/ch02-intro/linkage/*.csv"
val parsed = spark.read.
    option("header", "true").
    option("nullValue", "?").
    option("inferSchema", "true").
    csv(filepath)

parsed.show()
parsed.printSchema()
parsed.cache()

/*
There are two ways to refer to the column names, one is to directly
use literal strings and or as Column objects using the special $"<col>" syntax
*/
parsed.
groupBy("is_match").
count().
orderBy($"count".desc).
show()

// other operations apart from counting
parsed.agg(avg($"cmp_sex"), stddev($"cmp_sex")).show()

/*
We can also register a temporary table and query it using SQL like syntax
*/
parsed.createOrReplaceTempView("linkage")
spark.sql("""
    SELECT is_match, COUNT(*) count
    FROM linkage
    GROUP BY is_match
    ORDER BY count DESC
"""
).show()

val summary = parsed.describe()
summary.select("summary", "cmp_fname_c1", "cmp_fname_c2").show()

/*
To perform filtering, we can use SQL like statement that
would be valid inside the WHERE clause in Spark SQL;
The ===, triple `=` operator is use to see if two spark columns are equal
https://stackoverflow.com/questions/39490236/difference-between-and-in-scala-spark
*/
val matches = parsed.where("is_match = true")
val matchSummary = matches.describe()
val misses = parsed.filter($"is_match" === false)
val missSummary = misses.describe()

/*
Scala only: to extract the value from a Row object, we can use the .get* method,
here our fields are type String, thus it make sense to use .getString method;
or we can use .getAs method to use name or indices (e.g. getAs[String]("colname"))
https://stackoverflow.com/questions/33007840/spark-extracting-values-from-a-row
*/
val schema = summary.schema
val longForm = summary.flatMap(row => {
    val metric = row.getString(0)
    (1 until row.size).map(i => {
        (metric, schema(i).name, row.getString(i).toDouble)
    })
})

/*
DataFrame is an alias for Dataset[Row] type, it allows
spark to handle a richer set of data type than just
instances of Row class
*/
val longDF = longForm.toDF("metric", "field", "value")
longDF.show()

/*
pivoting gives the same information, just laid out differently
https://svds.com/pivoting-data-in-sparksql/
*/
val wideDF = longDF.
    groupBy("field").
    pivot("metric", Seq("count", "mean", "stddev", "min", "max")).
    agg(first("value"))


def pivotSummary(summary: DataFrame): DataFrame = {
    val schema = summary.schema
    val longDF = summary.flatMap(row => {
        val metric = row.getString(0)
        (1 until row.size).map(i => {
            (metric, schema(i).name, row.getString(i).toDouble)
        })
    }).toDF("metric", "field", "value")

    val wideDF = longDF.
        groupBy("field").
        pivot("metric", Seq("count", "mean", "stddev", "min", "max")).
        agg(first("value"))
    wideDF
}
val matchSummaryT = pivotSummary(matchSummary)
val missSummaryT = pivotSummary(missSummary)


/*
Peforming joins might be easier using the Spark SQL syntax, especially
when we want to be able to clearly indicate which columns are we joinging together
*/
matchSummaryT.createOrReplaceTempView("match")
missSummaryT.createOrReplaceTempView("miss")

/*
A good feature should have two properties:
1. it tends to have significantly different values for different labels
2. it occurs often enough in the data that we can rely on it to be available
*/
spark.sql("""
    SELECT 
        a.field,
        a.count + b.count total,
        a.mean - b.mean delta
    FROM
        match a
    INNER JOIN
        miss b
    ON
        a.field = b.field
    WHERE
        a.field NOT IN ("id_1", "id_2")
    ORDER BY
        delta DESC,
        total DESC
""").show()


/*
To abstract way Spark specific components of the model,
we want to be able to work with DataFrame of statically
typed variables as oppose to the Row class (this way
production code that simply does the scoring
won't depend that heavily on Spark)

Option[T] indicates that the data could be null,
thus it requires the end-user to check whether
a particular field is missing or not
*/
import org.apache.spark.sql.DataFrame
import org.apache.spark.sql.types.{StructType, StructField, StringType, IntegerType, DoubleType, BooleanType}
case class MatchData(
    id_1: Option[Int],
    id_2: Option[Int],
    cmp_fname_c1: Option[Double],
    cmp_fname_c2: Option[Double],
    cmp_lname_c1: Option[Double],
    cmp_lname_c2: Option[Double],
    cmp_sex: Option[Int],
    cmp_bd: Option[Int],
    cmp_bm: Option[Int],
    cmp_by: Option[Int],
    cmp_plz: Option[Int],
    is_match: Option[Boolean]
)

val customSchema = StructType(Array(
    StructField("id_1", IntegerType, true),
    StructField("id_2", IntegerType, true),
    StructField("cmp_fname_c1", DoubleType, true),
    StructField("cmp_fname_c2", DoubleType, true),
    StructField("cmp_lname_c1", DoubleType, true),
    StructField("cmp_lname_c2", DoubleType, true),
    StructField("cmp_sex", IntegerType, true),
    StructField("cmp_bd", IntegerType, true),
    StructField("cmp_bm", IntegerType, true),
    StructField("cmp_by", IntegerType, true),
    StructField("cmp_plz", IntegerType, true),
    StructField("is_match", BooleanType, true)
))


case class Score(value: Double) {
    def +(oi: Option[Int]) = {
        Score(value + oi.getOrElse(0))
    }
}


def scoreMatchData(md: MatchData): Double = {
    /*
    score starts with a double and merge the value
    into the running sum, we also leverge the .getOrElse
    by getting the value or returning 0 if it's missing
    */
    val score = Score(md.cmp_lname_c1.getOrElse(0.0))
    (score + md.cmp_plz + md.cmp_by + md.cmp_bd + md.cmp_bm).value
}


def crossTabs(scoreDF: DataFrame, threshold: Double): DataFrame = {
    /*
    Scala string interpolation syntax, where we preface
    the string with "s" and the variable that we wish to
    substitute as t
    */
    scoreDF.
    selectExpr(s"score >= $threshold as above", "is_match").
    groupBy("above").
    pivot("is_match", Seq("true", "false")).
    count()
}


val filepath = "/Users/ethen/programming/advanced_analytics_spark/ch02-intro/linkage/*.csv"
val parsed = spark.read.
    option("header", "true").
    option("nullValue", "?").
    schema(customSchema).
    csv(filepath)

// convert the data to the DataSet type
val matchData = parsed.as[MatchData]
val scoreDF = matchData.map(row =>
    (scoreMatchData(row), row.is_match)
).toDF("score", "is_match")
crossTabs(scoreDF, 4.0).show()

