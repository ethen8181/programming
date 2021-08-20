package org.example.akkastream

import java.util.Date

import akka.stream.scaladsl.Source

class AkkaStreamPractice5 extends AkkaStreamEnvironment {

    def execute1(): Unit = {
        case class PagerEvent(application: String, description: String, date: Date)

        val eventSource = Source(List(
            PagerEvent("infra", "broke", new Date),
            PagerEvent("data", "illegal element", new Date),
            PagerEvent("infra", "service outage", new Date),
            PagerEvent("frontend", "button doesn't work", new Date)
        ))

        object PagerService {
            val engineers = List("daniel", "john")
            val emails = Map(
                "daniel" -> "daniel@mail.com",
                "john" -> "john@mail.com"
            )

            
        }
    }
}

object AkkaStreamPractice5 extends App {
    val akkaStream = new AkkaStreamPractice5
    akkaStream.execute1()
}




