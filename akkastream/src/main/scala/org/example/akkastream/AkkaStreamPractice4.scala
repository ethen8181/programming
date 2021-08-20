package org.example.akkastream

import java.util.Date

import akka.stream.{ClosedShape, FlowShape, SinkShape, UniformFanOutShape}
import akka.stream.scaladsl.{Broadcast, Flow, GraphDSL, Merge, RunnableGraph, Sink, Source, Zip}

import scala.util.{Failure, Success}

/*
    Akka Stream API supports two types of graphs, the linear graph that can be created with
    the basic building blocks of Akka Streams (Source | Flow | Sink)

    Akka Stream GraphDSL are for building complex graphs. The building blocks here are
    Fan-In (multiple inputs, single output), Fan-Out (single input, multiple outputs)
    and edge operator.
    The GraphDSL will then translate our design diagram into Akka Stream source code.

    https://doc.akka.io/docs/akka/2.5.32/stream/stream-graphs.html
 */
class AkkaStreamPractice4 extends AkkaStreamEnvironment {

    val intSource = Source(1 to 1000)
    val addFlow = Flow[Int].map(_ + 1)
    val multiplyFlow = Flow[Int].map(_ * 10)
    val sink = Sink.foreach[Int](println)
    val zipSink = Sink.foreach[(Int, Int)](println)

    def execute1(): Unit = {

        // step 1 : set up the boiler plate for creating graph using GraphDSL
        val graph = RunnableGraph.fromGraph(
            GraphDSL.create() { implicit builder =>
                import GraphDSL.Implicits._

                /*
                    step 2 : we define the necessary components for our graphs here

                    we define the fan out operator using Broadcast, where we need
                    to specify the number of output ports. The operator will take
                    its input and copy it to each of its output

                     we define the fan in operator using Zip
                 */
                val broadcast = builder.add(Broadcast[Int](2))
                val zip = builder.add(Zip[Int, Int])

                /*
                     step 3 : tying up the components

                     GraphDSL.Implicits brings into scope, the ~> operator that gives us a way to
                     connect our components together
                 */
                intSource ~> broadcast

                broadcast ~> addFlow ~> zip.in0
                broadcast ~> multiplyFlow ~> zip.in1

                zip.out ~> zipSink

                /*
                    step 4 : we must return a shape object, in order to freeze our builder's shape

                    A closed graph means all input and output points are connected, and we can
                    directly run it
                 */
                ClosedShape
            }
        )

        graph.run()
    }

    def execute2(): Unit = {
        /*
            Sometimes it is not possible or needed to construct the entire computational graph
            in one place. We can construct different phases as "partial graphs" and connect them
            all together into a complete graph at the very end.

            This can be achieved by defining a different shape. Here we define a partial graph that
            has the flow shape.

            Broadcast is a fan-out operation and merge is a fan-in operation,
            where broadcast takes 1 input and emits the input element to each of the output
            and the merge operation takes n inputs and picks randomly push them one by one to its output
         */
        val broadcastMergeFlow = Flow.fromGraph(
            GraphDSL.create() { implicit builder =>
                import GraphDSL.Implicits._

                val broadcast = builder.add(Broadcast[Int](2))
                val merge = builder.add(Merge[Int](2))

                broadcast ~> addFlow ~> merge
                broadcast ~> multiplyFlow ~> merge

                FlowShape(broadcast.in, merge.out)
            }
        )

        val graph = intSource.via(broadcastMergeFlow).to(sink)
        graph.run
    }

    def execute3(): Unit = {
        /*
            Uniform shape in Akka Stream defines components where the input and output types are the
            same. If our application needs to push different types, then we will need non-uniform shape

            Say we are an e-commerce platform trying to detect potential money laundering,
            we will stream user transaction, where 1 sink will let all the transaction go through,
            and the other will flag suspicious transaction. Here our suspicious criteria will be
            a simple rule saying if the transaction amount if greater than a fix threshold.
         */

        // boilerplate setup
        case class Transaction(id: String, itemId: String, userId: String, amount: Int, date: Date)

        val transactionSource = Source(List(
            Transaction("t1", "i1", "u1", 100, new Date),
            Transaction("t2", "i2", "u2", 100000, new Date),
            Transaction("t3", "i3", "u3", 7000, new Date)
        ))

        val allSink = Sink.foreach[Transaction](transaction => println(s"all transaction: $transaction"))
        val suspiciousSink = Sink.foreach[Transaction](transaction => println(s"suspicious transaction: $transaction"))

        // creating the custom fan out operation
        val suspiciousTransactionStaticGraph = GraphDSL.create() { implicit builder =>
            import GraphDSL.Implicits._

            // e.g. broadcast is an uniform shape component
            val broadcast: UniformFanOutShape[Transaction, Transaction] = builder.add(Broadcast[Transaction](2))
            val suspiciousFilter = builder.add(Flow[Transaction].filter(transaction => transaction.amount >= 10000))

            broadcast.out(0) ~> suspiciousFilter

            /*
                as both the output branches are of the same type, the return shape is a uniform shape
                if the output type is different, then we would need to use non-uniform shape, i.e.
                replace UniformFanOutShape with new FanOutShape2
             */
            UniformFanOutShape(broadcast.in, suspiciousFilter.out, broadcast.out(1))
        }

        // creating the runnable graph
        val suspiciousTransactionRunnableGraph = RunnableGraph.fromGraph(
            GraphDSL.create() { implicit builder =>
                import GraphDSL.Implicits._

                val suspiciousTransaction = builder.add(suspiciousTransactionStaticGraph)

                transactionSource ~> suspiciousTransaction.in
                suspiciousTransaction.out(0) ~> suspiciousSink
                suspiciousTransaction.out(1) ~> allSink

                ClosedShape
            }
        )

        suspiciousTransactionRunnableGraph.run()
    }

    def execute4(): Unit = {
        // We can also expose materialized value through Graph DSL

        val source = Source(1 to 10)
        val sink = Sink.fold[Int, Int](0)((count, element) => count + 1)

        /*
            To do so, we pass in the sink as arguments to the GraphDSL.create() method,
            after doing so, the input becomes a high order function of builder => sink,
            then we can use the sink variable as is in our GraphDSL scope
         */
        val sinkGraph = Sink.fromGraph(
            GraphDSL.create(sink) { implicit builder => sink =>
                import GraphDSL.Implicits._

                val flow = builder.add(Flow[Int].filter(_ % 2 == 0))

                // Graph DSL is most likely an overkill for a linear flow
                flow ~> sink

                SinkShape(flow.in)
            }
        )

        val done = source.runWith(sinkGraph)
        done.onComplete {
            case Success(value) => println(s"total value: $value")
            case Failure(exception) => println(s"exception $exception")
        }
    }

}

object AkkaStreamPractice4 extends App {
    val akkaStream = new AkkaStreamPractice4
    akkaStream.execute4()
}


