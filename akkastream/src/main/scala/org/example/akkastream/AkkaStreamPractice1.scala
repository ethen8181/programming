package org.example.akkastream

import akka.{Done, NotUsed}
import akka.actor.ActorSystem
import akka.stream.ActorMaterializer
import akka.stream.scaladsl.{Flow, RunnableGraph, Sink, Source}

import scala.concurrent.Future

/*
    Akka Stream is a module built on top of Akka to make the ingestion and processing
    of streams easier using the actor model under the hood.

    Akka Stream follows the Reactive Stream standards. It has backpressure mechanism enabled
    by default, this features allow components to signal other components in the stream
    that they are ready to process new elements. If some part of the processing takes longer
    (e.g. inserting into a database or calling an API), we can throttle the consumer until
    things go back to normal. i.e. the Consumer can inform the Producer on the amount of data
    it can accept so that the Producer sends only that amount of data to avoid out of memory
    errors from occurring.

    Akka Stream core concepts:

    Source : the entry point to processing. We can create an instance of this class
    from various sources. In Reactive Stream standards, this is the publisher, which emits
    elements asynchronously.

    Flow : building blocks for processing. Every Flow has 1 input and 1 output, it is
    used as a connector between Source and Sink to process the elements in between.
    In Reactive Stream standards, this is the processor.

    Materializer : we can use one if we want our Flow to have some side effects like
    logging or saving results, NotUsed is use to denote our Flow should not have any
    side effects

    Sink : when we are building a Flow, it won't be executed until we register a Sink,
    it serves as a operation that triggers all the computations in the entire Flow. In
    Reactive Stream standards, this is the subscriber. This component receives elements,
    and won't terminate

    Source and Sink are special cases of the Flow element and the difference is whether
    the output is open (Source) or the input (Sink).

    We use connect these components using the Akka stream APIs to build our reactive
    streaming application

    https://scalac.io/streams-in-akka-scala-introduction/
 */
class AkkaStreamPractice1 {

    def execute1(): Unit = {
        /*
            The system and materializer are implicit variables that are needed to run the stream.

            ActorMaterializer is responsible for creating the underlying Akka Actors with the specific
            functionality we've defined in our code.

            By default, the Akka Stream API uses ActorMaterializer to execute our data flow graphs
            (Graph or RunnableGraph).
            Hence as developers, we specify the Akka Stream data flow graphs, then the ActorMaterializer
            is responsible for transforming these into low level reactive streams, as well as
            executing those graphs and providing the results (materialized value)
         */
        implicit val system = ActorSystem("Practice1")

        // materializer accepts the implicit system
        implicit val materializer = ActorMaterializer()

        /*
            We'll create a source that will iterate over a sequence of numbers
            the first type parameter is the type of data the source emits and the second
            is the auxiliary value it can produce. Here, we are not producing any, hence we
            use the NotUsed type provided by Akka
        */
        val source: Source[Int, NotUsed] = Source(1 to 100)

        /*
           We then create a Flow that only let even numbers through. Flow is basically
           a way of transforming its input.
           it takes three type parameter, first the input type, second for the output type
           and last one for auxiliary type
        */
        val flow: Flow[Int, Int, NotUsed] = Flow[Int].filter(_ % 2 == 0)

        /*
            Finally, we have a sink that will write its inputs onto the console.

            Here the foreach method invokes the defined procedure for each received element.
         */
        val sink: Sink[Int, Future[Done]] = Sink.foreach[Int](println)

        /*
            Given the three components, we create our akka stream graph by
            connecting source with flow using the .via syntax,
            and source or source with flow to a sink using the .to syntax
         */

        val graph: RunnableGraph[NotUsed] = source
            .via(flow)
            .to(sink)

        /*
            The graph is static until we trigger it,
            running this graph is also called materializing the graph
            .run accepts the implicit materializer
         */
        graph.run()
    }
}


object AkkaStreamPractice1 extends App {
    val akkaStream = new AkkaStreamPractice1
    akkaStream.execute1()
}
