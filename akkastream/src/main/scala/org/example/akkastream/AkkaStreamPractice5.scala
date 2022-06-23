package org.example.akkastream

import akka.stream.scaladsl.{Sink, Source}

import scala.concurrent.duration._

/*
    https://blog.colinbreck.com/partitioning-akka-streams-to-maximize-throughput/
 */
class AkkaStreamPractice5 extends AkkaStreamEnvironment {

    def execute1(): Unit = {
        /*
            We can perform classic map-reduce like flows with akka stream.
            grouping a stream by a certain function creates a sub-stream,
            we define our operations on each sub-stream, at the end, call
            mergeSubStream to "reduce" them.

            When using groupby, the addition of async before the mergeSubStream
            remains an important thing to test, this groupBy example is similar
            to using a Partition operation in Akka Stream's Graph DSL.

            When using groupBy it's important to note that we have to specify the
            maxSubstreams parameter. Akka stream is focused on bounded resource
            consumption, if the groupBy operator encounters more keys than the
            specified number, then the stream will terminate with a failure.
         */

        val wordSource = Source(List(1, 2, 3, 4, 5, 6, 7, 8))
        wordSource
            .groupBy(4, _ % 4)
            .map { element =>
                element + 1
            }
            .async
            .mergeSubstreams
            .to(Sink.foreach[Int](println))
            .run
    }

    def execute2(): Unit = {
        /*
            Batching Messages, when working with streaming messages, one common
            operation is to write incoming records to another database. Rather than
            writing a single record at a time, it is often times more efficient to
            write batches of records to reduce the number of external requests that
            are made. While doing grouping, it is also important that last records
            are made available in a timing manner.

            Akka stream provides a groupedWithin that groups the batches in the batch size
            we specify or how much it can batch over the duration we've specified.

            Example use case:
            - https://siddharthkhialani.wordpress.com/2020/06/08/my-first-time-using-akka-streams/
            - https://blog.colinbreck.com/patterns-for-streaming-measurement-data-with-akka-streams/
         */

        val source = Source(1 to 10000)
        source
            .groupedWithin(100, 100.milliseconds)
            .map { batchedElement =>
                println(batchedElement)
            }
            .runWith(Sink.ignore)
    }
}

object AkkaStreamPractice5 extends App {
    val akkaStream = new AkkaStreamPractice5
    akkaStream.execute1()
}
