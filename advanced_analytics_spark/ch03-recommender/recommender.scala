import scala.util.Random
import org.apache.spark.sql._
import org.apache.spark.broadcast._
import org.apache.spark.ml.recommendation._


val basepath = "/Users/ethen/programming/advanced_analytics_spark/ch03-recommender/profiledata_06-May-2005/"
val filepath = basepath + "user_artist_data.txt"

/*
Because machine learning task are generally more computationally
expensive than simple text preprocessing. It may be better to break
the data into smaller pieces, i.e. more partitions for processing.
We can call .repartition after reading the file in to change the
number of partitions
*/
val rawUserArtistData = spark.read.textFile(filepath)
rawUserArtistData.take(5).foreach(println)


/*
flatMap works really well with Option class since it either maps
to zero, one or more result. And Option represents a value that
optionally exists. Where Some corresponds the result that does exist
and None represents that one that doesn't
*/
def buildartistByID(rawArtistData: Dataset[String]): DataFrame = {
    rawArtistData.flatMap { line =>
        /*
        .span allows us the split the stream of String into two parts by
        providing a function that detects the splitting criteria
        https://www.garysieling.com/blog/scala-span-example
        */
        val (id, name) = line.span(_ != '\t')

        // test whether a string is empty
        if (name.isEmpty) {
            None
        } else {
            try {
                Some((id.toInt, name.trim))
            } catch {
               case _: NumberFormatException => None
            }
        }
    }.toDF("id", "name")
}
val rawArtistData = spark.read.textFile(basepath + "artist_data.txt")
val artistByID = buildartistByID(rawArtistData)


/*
Create a broadcast variable so Spark will send and hold in memory just
one copy for each executor in the cluster
*/
def buildArtistAlias(rawArtistAlias: Dataset[String]): Map[Int, Int] = {
    rawArtistAlias.flatMap { line =>
        val Array(artist, alias) = line.split('\t')
        if (artist.isEmpty) {
            None
        } else {
            Some((artist.toInt, alias.toInt))
        }
    }.collect().toMap
}
val rawArtistAlias = spark.read.textFile(basepath + "artist_alias.txt")
val artistAlias = buildArtistAlias(rawArtistAlias)
val artistAliasBroadcast = spark.sparkContext.broadcast(artistAlias)


def buildCount(rawUserArtistData: Dataset[String],
               artistAliasBroadcast: Broadcast[Map[Int, Int]]): DataFrame = {
    // map the artist to their alias id
    rawUserArtistData.map { line =>
        val Array(userID, artistID, count) = line.split(" ").map(_.toInt)
        val artistAliasID = artistAliasBroadcast.value.getOrElse(artistID, artistID)
        (userID, artistAliasID, count)
    }.toDF("user", "artist", "count")
}

// construct dataset & train/test split
val allData = buildCount(rawUserArtistData, artistAliasBroadcast)
val Array(trainData, testData) = allData.randomSplit(Array(0.9, 0.1))
trainData.cache()
testData.cache()


// model training
val model = new ALS().
    setSeed(Random.nextLong()).
    setImplicitPrefs(true).
    setRank(10).
    setRegParam(0.01).
    setAlpha(1.0).
    setMaxIter(5).
    setUserCol("user").
    setItemCol("artist").
    setRatingCol("count").
    setPredictionCol("prediction").
    fit(trainData)


// TODO: AUC evaluation
val allArtistID = allData.
    select("artist").as[Int].
    distinct().
    collect
val allArtistIDBroadcast = spark.sparkContext.broadcast(allArtistID)



/*
Benchmark this against a simpler approach. e.g. recommending the globally
most-played artists to every user
*/

val userID = 2093760
val existingArtistIDs = trainData.
    filter($"user" === userID).
    select("artist").as[Int].
    collect

// _* varargs syntax of unpacking multiple elements in the Array
artistByID.filter($"id" isin (existingArtistIDs: _*)).show()


def makeRecommendation(model: ALSModel, userID: Int, topn: Int): DataFrame = {
    /*
    The input item column's name is artist, thus
    we select the item id column and pair it with
    one user id
    */
    val toRecommend = model.itemFactors.
        select($"id".as("artist")).
        withColumn("user", lit(userID))

    // very crude way to sort the top-n recommendation
    model.
    transform(toRecommend).
    select("artist", "prediction").
    orderBy($"prediction".desc).
    limit(topn)
}
val topRecommendations = makeRecommendation(model, userID, 5)
topRecommendations.show()

val recommendedArtistIDs = topRecommendations.
    select("artist").as[Int].
    collect()

artistByID.filter($"id" isin (recommendedArtistIDs:_*)).show()


/*
collect some user to the driver and make recommendations, since
Spark 2.2 there is a .recommendForAllUsers and .recommendForAllItems method
*/
val someUsers = allData.select("user").as[Int].distinct().take(10)
val someRecommendations = someUsers.
    map(userID => (userID, makeRecommendation(model, userID, topn = 5)))

// looping over Array by unpacking each element using case(element1, element2)
someRecommendations.foreach { case(userID, recDF) =>
    val recommendedArtists = recDF.select("artist").as[Int].collect()
    /* 
    mkString: joins a collection together with a delimiter,
    here the recommendations are just printed, but they can be
    written to external NOSQL database to provide fast lookup at runtime
    */
    println(s"$userID -> ${recommendedArtists.mkString(", ")}")
}
