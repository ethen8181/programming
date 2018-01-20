package example

import akka.actor.Props
import akka.actor.Actor
import akka.actor.ActorSystem

// https://www.scala-lang.org/documentation/getting-started-intellij-track/building-a-scala-project-with-intellij-and-sbt.html
// https://github.com/izmailoff/SmallAkkaProjectExample

// here our actor takes one constructor parameter
class HelloActor(var myName: String) extends Actor {
    // its behavior is implemented by defining a receive method
    // and using the match expression to handle all potential
    // messages that's send to the actor
    override def receive = {
        case "hello" => println(s"hello from $myName")
        case _ => println(s"huh?, said $myName")
    }
}

object Main extends App {

    // create the system and give it a meaningful name;
    // this is a group of actors that shares the same configuration
    // thus we usually create one per application
    val system = ActorSystem("HelloSystem")

    // create the actual actor at the ActorSystem level by passing our
    // actor's class name to the system.actorOf method using the Props case class
    // actors are automatically started when created, thus there's no need
    // to call any sort of start or run method. This actorOf method
    // returns a ActorRef, which is facade between the end user and the
    // actual actor.
    // If our actor whose constructor takes zero argument, we can define it
    // as Props[HelloActor]
    val helloActor = system.actorOf(Props(new HelloActor("Fred")), name = "helloactor")

    // send the actor two messages with the ! method
    // the helloActor will respond accordingly
    helloActor ! "hello"
    helloActor ! "buenos dias"

    // shut down the system, if we do not
    // call shutdown, our application will run indefinitely
    system.shutdown

    val ages = Seq(12, 15, 20, 23)
    println(s"the oldest person's age ${ages.max}")
}
