package org.example.akkastream

import akka.{Done, NotUsed}
import akka.actor.ActorSystem
import akka.stream.{ActorMaterializer, OverflowStrategy}
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

    - https://blog.colinbreck.com/maximizing-throughput-for-akka-streams/
    - https://blog.colinbreck.com/patterns-for-streaming-measurement-data-with-akka-streams/
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

            Unlike a normal fused execution flow, where an element in our stream completely
            passes through the processing components before the next element enters
            the flow, the next element is processed as soon as the component has emitted
            the previous element.

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
        /*
            When a stream has a stage that performs a relatively expensive operation and introducing an
            asynchronous boundary with async does not introduce sufficient parallelism, capturing the work
            in a Future, and using mapAsync, can significantly increase throughput, by further increasing
            parallelism and saturating the available cores. Future will most likely execute on another
            thread of the execution context, or even on a separate execution context.

            The function that we pass to mapAsync returns a Future, hence it is asynchronous.
            This method accepts a parallelism parameter determining how many future can run at
            the same time. For non CPU bound workload, like network I/O, throughout may be
            improved by increasing this parameter to a number that's well beyond the number of
            available cores to keep downstream task saturated with workloads.

            async and mapAsync are both means of introducing asynchronous flows. The difference is
            mapAsync works with Future, meaning the workload will be executed on a thread of the
            execution context, rather than by the actor executing the flow stage, but unlike async,
            it does not introduce asynchronous boundary into a flow, the stages are still fused an
            executed by the same underlying actor.

            mapAsyncUnordered : mapAsync guarantees the relative order of incoming elements, if we
            don't need this behaviour, then we can use mapAsyncUnordered. If there is a lot of variation
            in how long each Future takes to complete and preserving downstream ordering is not important,
            mapAsyncUnordered can be used to increase the throughout and more effectively saturate
            downstream stages, by emitting a Future as soon as it completes, independent of the overall
            ordering of the stream.

            If we use Future in our streams, we should run them in their own execution context, not
            on the actor system dispatcher, because we may starve it for threads
         */

        /*
            the parallelism parameter for mapAsync also acts as a rate limiter, where we can control
            the number of concurrent requests to other services to strike a good balance between
            throughout and not overwhelming them
         */
        val done = intSource
            .mapAsync(2)(taskFuture)
            .mapAsync(2)(taskFuture)
            .runWith(printSink)

        done.onComplete {
            case Success(value) => println(s"total value: $value")
            case Failure(exception) => println(s"exception $exception")
        }
    }

    def taskFuture(value: Int): Future[Int] = Future {
        Thread.sleep(1000)
        value + 1
    }

    def execute4(): Unit = {
        /*
            When the asynchronous boundary is introduced, Akka Stream inserts a buffer
            between every asynchronous processing stage to support a windowed
            backpressure strategy, new elements are requested in batches to amortize
            the cost of requesting elements across the asynchronous boundary between
            flow stage.

            Back pressure is one of the fundamental features of reactive streams. This
            is built in to all provided akka stream operators, hence it is transparent
            to the library's end user.

            Rate in which elements flows through our stream is response to the consumer's demand
            i.e. if we have a slow consumer/sink. Then the consumer will send a signal upstream,
            potentially buffering elements in our flow, or potentially going all the way to the
            producer/source, telling it to slow down.

            We can explicitly specify the buffer ourselves, and sometimes this can be crucial
            to achieving a good throughout
         */

        val done = intSource
            .buffer(100, OverflowStrategy.backpressure)
            .mapAsync(2)(taskFuture)
            .runWith(printSink)

        done.onComplete {
            case Success(value) => println(s"total value: $value")
            case Failure(exception) => println(s"exception $exception")
        }
    }
}

object AkkaStreamPractice3 extends App {
    val akkaStream = new AkkaStreamPractice3
    akkaStream.execute4()
}
