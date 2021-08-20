package org.example.akkastream

import akka.{Done, NotUsed}
import akka.actor.ActorSystem
import akka.stream.ActorMaterializer
import akka.stream.scaladsl.{Flow, Sink, Source}

import scala.concurrent.Future
import scala.util.{Failure, Success}

trait AkkaStreamEnvironment {
    implicit val system = ActorSystem("Practice3")
    implicit val materializer = ActorMaterializer()
    implicit val executionContextExecutor = system.dispatcher
}

/*
    When we construct a akka stream runnable graph, by default it will
    be run on the same actor, as akka stream performs operator fusion
    underneath the hood. These fused stream do not run in parallel, meaning
    only up to one CPU core is used for each fused part.

    This works great for small task, but if we have costly operations in our flow,
    we can inject asynchronous boundaries into our flows.

    https://blog.colinbreck.com/maximizing-throughput-for-akka-streams/
 */
class AkkaStreamPractice3 extends AkkaStreamEnvironment {

    val intSource: Source[Int, NotUsed] = Source(1 to 1000)

    // simulate a heavy task
    val taskFlow: Flow[Int, Int, NotUsed] = Flow[Int].map { value =>
        Thread.sleep(1000)
        value + 1
    }

    val printSink: Sink[Int, Future[Done]] = Sink.foreach[Int](println)

    def execute1(): Unit = {

        // a linear akka stream flow that serves as a baseline
        val done: Future[Done] = intSource
            .via(taskFlow)
            .via(taskFlow)
            .runWith(printSink)

        done.onComplete {
            case Success(value) => println(s"total value: $value")
            case Failure(exception) => println(s"exception $exception")
        }
    }

    def execute2(): Unit = {
        /*
            To allow for parallel processing, we will have to insert asynchronous
            boundaries manually into our flows using the method .async. This means
            each map stage will be will executed in a separate actor, with
            asynchronous message passing used to communicate between the actors.

            When the asynchronous boundary is introduced, Akka Stream inserts a buffer
            between every asynchronous processing stage to support a windowed
            backpressure strategy, new elements are requested in batches to amortize
            the cost of requesting elements across the asynchronous boundary between
            flow stage.

            Back pressure is one of the fundamental features of reactive streams. This
            is built in to all provided akka stream operators, hence it is transparent
            to the end user of the library.

            Rate in which elements flows through our stream is response to the demand
            from the consumer. i.e. if we have a slow consumer/sink. Then the consumer
            will send a signal upstream, potentially buffering the elements in our flow,
            or potentially going all the way to the producer/source, telling it to slow down.

            Notice that we can experiment with the parallelism option by simply
            adding .async to our flow. In traditional multi-threaded programming,
            we might need to write a lot of threading related code to even run
            such an experiment. Like all parallelism, make sure to experiment to see
            if like actually increased the throughout, don't blindly introduce it
            everywhere as if the workload is not expensive, the additional overhead
            of parallelism will actually degrade the performance.
        */
        val done = intSource
            .via(taskFlow)
            .async
            .via(taskFlow)
            .async
            .runWith(printSink)

        done.onComplete {
            case Success(value) => println(s"total value: $value")
            case Failure(exception) => println(s"exception $exception")
        }
    }

    def execute3(): Unit = {
    }
}

object AkkaStreamPractice3 extends App {
    val akkaStream = new AkkaStreamPractice3
    akkaStream.execute3()
}
