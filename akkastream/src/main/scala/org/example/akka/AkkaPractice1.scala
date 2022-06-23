package org.example.akka

import akka.actor.{Actor, ActorSystem, Props}

/*
    With Class that we are typically familiar with.
    We can store internal state/data in them, and we interact with them
    by calling associated methods.

    With Actors, we also store internal state/data in them, but the way we
    interact with actors is by sending messages to them
 */

class AkkaPractice1 {

    implicit val system = ActorSystem("Practice1")

    def execute1(): Unit = {

        // we define a actor by extending from the Actor trait
        class WordCountActor extends Actor {
            // internal state
            var totalWords = 0

            /*
                over-ride the receive method and define the intended behaviour.
                note the incoming message can be of any-type. The Receive type is
                a type alias for a partial function of any to unit.

                In 99.9% of the cases, it's usually one of primitive types, case
                classes or case objects.
             */
            override def receive: Receive = {
                case message: String =>
                    totalWords += message.split(" ").length
                    println(s"total words: $totalWords")
            }
        }

        /*
            we use a special boilerplate way of creating an actor, using the actorOf factory
            method from ActorSystem. Note the new needs to be inside the Props apply method.
            Passing name in the second argument allows us to uniquely identify an actor.
         */
        val wordCountActor = system.actorOf(Props(new WordCountActor), "wordCountActor")

        // we communicate to the actor by using the "!" method, a.k.a the tell method
        wordCountActor ! "I am learning akka"
    }
}

object AkkaPractice1 extends App {
    val akkaPractice1 = new AkkaPractice1
    akkaPractice1.execute1()
}
