import org.apache.spark.sql.DataFrame
import org.apache.spark.sql.functions._
import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.ml.{Pipeline, PipelineModel}
import org.apache.spark.ml.feature.VectorAssembler
import org.apache.spark.ml.classification.DecisionTreeClassifier
import org.apache.spark.ml.evaluation.MulticlassClassificationEvaluator
import org.apache.spark.ml.tuning.{ParamGridBuilder, TrainValidationSplit}
import org.apache.spark.ml.linalg.Vector
import scala.util.Random


val spark = SparkSession.builder().getOrCreate()

val basepath = "/Users/ethen/programming/advanced_analytics_spark/ch04-rdf/"
val dataWithoutHeader = spark.read.
    option("inferSchema", true).
    option("header", false).
    csv(basepath + "covtype.data")

// ++ for concatenating collections
val colNames = Seq(
    "Elevation", "Aspect", "Slope",
    "Horizontal_Distance_To_Hydrology", "Vertical_Distance_To_Hydrology",
    "Horizontal_Distance_To_Roadways",
    "Hillshade_9am", "Hillshade_Noon", "Hillshade_3pm",
    "Horizontal_Distance_To_Fire_Points"
) ++ (
    (0 until 4).map(i => s"Wilderness_Area_$i")
) ++ (
    (0 until 40).map(i => s"Soil_Type_$i")
) ++ Seq("Cover_Type")

// the cast of target variable to double is required for spark ML
val data = dataWithoutHeader.
    toDF(colNames: _*).
    withColumn("Cover_Type", $"Cover_Type".cast("double"))


val Array(trainData, testData) = data.randomSplit(Array(0.9, 0.1))
trainData.cache()
testData.cache()


/*
1. Exclude the target from the feature vector
2. VectorAssembler is a Transformer that can be connected
with other Transformer to form a Pipeline
*/
val inputCols = trainData.columns.filter(_ != "Cover_Type")
val assembler = new VectorAssembler().
    setInputCols(inputCols).
    setOutputCol("featureVector")

// adds a new column of the vectorize-assembled input features
val assembledTrainData = assembler.transform(trainData)
assembledTrainData.select("featureVector").show(truncate = false)


val classifier = new DecisionTreeClassifier().
    setSeed(Random.nextLong()).
    setLabelCol("Cover_Type").
    setFeaturesCol("featureVector").
    setPredictionCol("prediction")

// use a fitted model and transform the original dataset
val model = classifier.fit(assembledTrainData)
val predictions = model.transform(assembledTrainData)
println(model.toDebugString)

// print out feature importance
model.featureImportances.
toArray.zip(inputCols).
sorted.reverse.foreach(println)

// check label, predicted class and probability
predictions.
select("Cover_Type", "prediction", "probability").
show(truncate = false)

/* check the baseline: 
summing the product of the probability from the training set
and test set
*/
def classProba(data: DataFrame): Array[Double] = {
    val total = data.count()
    data.
    groupBy("Cover_Type").
    count().
    orderBy("Cover_Type").
    select("count").as[Double].  // convert to dataset
    map(_ / total).
    collect()
}
val trainPriorProba = classProba(trainData)
val testPriorProba = classProba(testData)
trainPriorProba.zip(testPriorProba).map {
    case (trainProba, testProba) => trainProba * testProba
}.sum

// evaluation
val evaluator = new MulticlassClassificationEvaluator().
    setLabelCol("Cover_Type").
    setPredictionCol("prediction")

evaluator.setMetricName("accuracy").evaluate(predictions)
evaluator.setMetricName("f1").evaluate(predictions)


// apart from a single number summary, sometimes it's also
// useful to look at confusion matrix
val confusionMatrix = predictions.
    groupBy("Cover_Type").
    pivot("prediction", (1 to 7)).
    count().
    na.fill(0.0).
    orderBy("Cover_Type")

confusionMatrix.show()


/* 
pipeline way of performing cross validation
1. define the vector assembler and classifier
2. define the param grid of hyperparameters and
the evaluation metric to determine which configuration is best
3. choose a TrainValidation or CrossValidator to do a train/valid
split of choosing hyperparameters (CrossValidator may be too expensive
in the context of big data)
*/
val pipeline = new Pipeline().setStages(Array(assembler, classifier))
val paramGrid = new ParamGridBuilder().
    addGrid(classifier.impurity, Seq("gini", "entropy")).
    addGrid(classifier.maxDepth, Seq(1, 20)).
    addGrid(classifier.maxBins, Seq(40, 300)).
    addGrid(classifier.minInfoGain, Seq(0.0, 0.05)).
    build()
val multiclassEval = new MulticlassClassificationEvaluator().
    setLabelCol("Cover_Type").
    setPredictionCol("prediction").
    setMetricName("accuracy")
val validator = new TrainValidationSplit().
    setSeed(Random.nextLong()).
    setEstimator(pipeline).
    setEvaluator(multiclassEval).
    setEstimatorParamMaps(paramGrid).
    setTrainRatio(0.9)
val validatorModel = validator.fit(trainData)

// report the accuracy of the model for each hyperparameter combination
val paramsAndMetrics = validatorModel.validationMetrics.
    zip(validatorModel.getEstimatorParamMaps).sortBy(_._1).reverse

// case is used for tuple matching
paramsAndMetrics.foreach { case (metric, params) =>
    println(metric)
    println(params)
    println()
}

/*
extract parameters of the best model 
The fitted model from a Pipeline is a PipelineModel,
which consists of fitted models and transformers,
corresponding to the pipeline stages
*/
val bestModel = validatorModel.bestModel
bestModel.asInstanceOf[PipelineModel].stages.last.extractParamMap

// evaluate and compare the performance of the best model and the test set
validatorModel.validationMetrics.max
multiclassEval.evaluate(bestModel.transform(testData))


def unencodeOneHot(data: DataFrame): DataFrame = {
    val unhotUDF = udf((vec: Vector) => vec.toArray.indexOf(1.0).toDouble)

    /*
    Assemble the one-hot encoded columns into 1 and drop them all at once
    by replacing them with the numeric representation using our own user
    defined function
    */
    val wildernessCols = (0 until 4).map(i => s"Wilderness_Area_$i").toArray
    val wildernessAssembler = new VectorAssembler().
        setInputCols(wildernessCols).
        setOutputCol("wilderness")
    val withWilderness = wildernessAssembler.
        transform(trainData).
        drop(wildernessCols: _*).  // drop the one-hot columns
        withColumn("wilderness", unhotUDF($"wilderness"))  // overwrite with numeric column

    val soilCols = (0 until 40).map(i => s"Soil_Type_$i").toArray
    val soilAssembler = new VectorAssembler().
        setInputCols(soilCols).
        setOutputCol("soil")

    soilAssembler.
    transform(withWilderness).
    drop(soilCols: _*).
    withColumn("soil", unhotUDF($"soil"))
}
val unencTrainData = unencodeOneHot(trainData)
val unencTestData = unencodeOneHot(testData)
