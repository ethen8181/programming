package example

import akka.actor.Props
import akka.actor.Actor
import akka.actor.ActorSystem

// A case class can take arguments, so each instance of the case class
// can be different based on the value of its argument, on the other hand,
// case object does not take args in the constructor, hence there can only
// be one instance; often used for pattern matching
// https://stackoverflow.com/questions/32078526/difference-between-case-class-and-case-object/32078685#32078685
case object ForceRestart

class Kenny extends Actor {
    println("entered the kenny constructor")

    override def preStart(): Unit = { println("kenny: preStart") }

    // called after an actor is stopped, can be used to perform any cleanup work
    override def postStop(): Unit = { println("kenny: postStop") }

    override def preRestart(reason: Throwable, message: Option[Any]): Unit = {
        println("kenny: preRestart")
        println(s"MESSAGE: ${message.getOrElse("")}")
        println(s"REASON: ${reason.getMessage}")
        super.preRestart(reason, message)
    }

    // when a new actor is invoked with the exception
    override def postRestart(reason: Throwable) {
        println("kenny: postRestart")
        println(s"REASON: ${reason.getMessage}")
        // the default postRestart calls preRestart
        super.postRestart(reason)
    }

    override def receive = {
        case ForceRestart => throw new Exception("Boom!")
        case _ => println("Kenny received a message")
    }
}

object LifecycleDemo extends App {
    val system = ActorSystem("LifecycleDemo")
    val kenny = system.actorOf(Props[Kenny], name = "Kenny")

    println("sending kenny a simple String message")
    kenny ! "hello"
    Thread.sleep(1000)

    println("make kenny restart")
    kenny ! ForceRestart
    Thread.sleep(1000)

    // we can stop the actor before shutting the system
    println("stopping kenny")
    system.stop(kenny)

    println("shutting down system")
    system.shutdown
}
