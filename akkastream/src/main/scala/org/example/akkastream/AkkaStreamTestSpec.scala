package org.example.akkastream

import akka.actor.ActorSystem
import akka.stream.ActorMaterializer
import akka.stream.scaladsl.{Flow, Keep, Sink, Source}
import akka.stream.testkit.TestSubscriber
import akka.stream.testkit.scaladsl.{TestSink, TestSource}
import akka.testkit.TestKit
import org.scalatest.{BeforeAndAfterAll, WordSpecLike}

import scala.concurrent.Await
import scala.concurrent.duration._

// https://doc.akka.io/docs/akka/current/stream/stream-testkit.html#streams-testkit
class AkkaStreamTestSpec extends TestKit(ActorSystem("AkkaStreamTestSpec")) with WordSpecLike with BeforeAndAfterAll {
    implicit val materializer = ActorMaterializer()

    override def afterAll(): Unit = TestKit.shutdownActorSystem(system)

    "A simple stream" should {
        "satisfy basic assertion" in {
            // one way of testing our Akka stream code is to extract the materialized value and assert it

            val source = Source(1 to 10)
            val sink = Sink.fold[Int, Int](0)((a, b) => a + 1)
            val count = source.runWith(sink)
            val countResult = Await.result(count, 10.seconds)
            assert(countResult == 10)
        }

        "integrate with Streams Testkit sink" in {
            val source = Source(1 to 5)
            val testSink = TestSink.probe[Int]
            val materializedValue: TestSubscriber.Probe[Int] = source.runWith(testSink)

            // integrating with the testSink gives us additional methods such as manually controlling
            // the demand, as well as asserting over the elements coming downstream
            materializedValue
                .request(5)
                .expectNext(1, 2,3, 4, 5)
                .expectComplete()
        }

        "test flows with a test source and sink" in {
            val flowUnderTest = Flow[Int].map(_ * 2)
            val testSource = TestSource.probe[Int]
            val testSink = TestSink.probe[Int]

            val (publisher, subscriber) = testSource.via(flowUnderTest).toMat(testSink)(Keep.both).run()
            publisher
                .sendNext(1)
                .sendNext(2)
                .sendNext(3)
                .sendComplete()

            subscriber
                .request(3)
                .expectNext(2, 4, 6)
                .expectComplete()
        }
    }
}
