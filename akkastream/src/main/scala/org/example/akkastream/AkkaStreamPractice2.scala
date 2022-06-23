package org.example.akkastream

import akka.NotUsed
import akka.actor.ActorSystem
import akka.stream.ActorMaterializer
import akka.stream.scaladsl.{Flow, Keep, RunnableGraph, Sink, Source}

import scala.concurrent.Future
import scala.util.{Failure, Success}

/*
    Materializing values.

    Akka Stream have two different kinds of value, the value that flows
    within the Stream, as well as value that is produced and visible outside
    the Stream.
    If we want our stream to produce a value that we can access, we will need
    to materialize it, else nothing outside of our Stream will be able to peek
    into the value.

    https://manuel.bernhardt.io/2017/05/22/akka-streams-notused/
 */
class AkkaStreamPractice2 {

    def execute1(): Unit = {
        implicit val system = ActorSystem("Practice2")
        implicit val materializer = ActorMaterializer()
        import system.dispatcher

        val source = Source(1 to 10)
        val flow = Flow[Int].filter(_ % 2 == 0)

        // e.g. for our sink, we wish to count the total number of records that we've processed
        val sink: Sink[Int, Future[Int]] = Sink.fold[Int, Int](0)((count, element) => count + 1)

        /*
            to materialize the value, we can use the toMat (to materialize) syntax in conjunction
            with Keep.right.

            Keep.right says we would like to keep the value on the right side of
            the stream. Here it is the value that's coming out of the sink.
         */
        val graph1: RunnableGraph[Future[Int]] = source.via(flow).toMat(sink)(Keep.right)

        /*
            If we just wanted our flow to run, pushing elements from once place to
            another, then we will use NotUsed as a way of saying, we don't care about
            the materialized value.

            graph2 and graph3 are equivalent to each other.
         */
        val graph2: RunnableGraph[NotUsed] = source.via(flow).toMat(sink)(Keep.left)
        val graph3: RunnableGraph[NotUsed] = source.via(flow).to(sink)

        // we need to execution context, system.dispatcher, as Future needs the implicit variable
        val done: Future[Int] = graph1.run()
        done.onComplete {
            case Success(value) => println(s"total value: $value")
            case Failure(exception) => println(s"exception $exception")
        }
    }

    def execute2(): Unit = {
        /*
            akka stream offers many syntactic sugars. e.g.

            .toMat(sink)(Keep.right).run() is equivalent to .runWith(sink)
         */
        implicit val system = ActorSystem("Practice2")
        implicit val materializer = ActorMaterializer()
        import system.dispatcher

        val source = Source(1 to 10)
        val flow = Flow[Int].filter(_ % 2 == 0)
        val sink = Sink.fold[Int, Int](0)((a, b) => a + 1)
        val graph = source.via(flow)
        val done: Future[Int] = graph.runWith(sink)
        done.onComplete {
            case Success(value) => println(s"total value: $value")
            case Failure(exception) => println(s"exception $exception")
        }
    }
}

object AkkaStreamPractice2 extends App {
    val akkaStream = new AkkaStreamPractice2
    akkaStream.execute2()
}
