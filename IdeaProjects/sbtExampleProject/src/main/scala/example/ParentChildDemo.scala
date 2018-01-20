package example

import akka.actor.{Actor, ActorSystem, PoisonPill, Props}

case class CreateChild (name: String)
case class Name (name: String)

class Child extends Actor {
    var name = "no name"
    override def receive = {
        // it uses the Name case class to send the name field
        case Name(name) => this.name = name
        case _ => println(s"Child $name got message")
    }

    override def postStop(): Unit = {
        // self refers to the actor itself
        // https://stackoverflow.com/questions/7987561/what-is-self-in-akka
        println(s"They killed me, $name: ${self.path}")
    }
}

class Parent extends Actor {
    override def receive = {
        case CreateChild(name) =>
            println(s"parent about to create child $name ...")
            // the process of creating child actor from within another
            // actor is almost identical to the process of creating
            // a system-level actor. The only difference is we call the
            // actorOf method on the context object
            val child = context.actorOf(Props[Child], name = s"$name")
            child ! Name(name)
        case _ => println(s"Parent got some other message.")
    }
}

object ParentChildDemo extends App {
    val actorSystem = ActorSystem("ParentChildTest")
    val parent = actorSystem.actorOf(Props[Parent], name = "Parent")

    // send messages to Parent to create child actors
    parent ! CreateChild("Jonathan")
    parent ! CreateChild("Jordan")
    Thread.sleep(500)

    // lookup Jonathan, then kill it,
    // sending a PoisonPill is one way to stop Akka actors;
    // the PoisonPill message lets the actor process all messages
    // that are in the mailbox ahead of it before stopping, thus
    // any message after actor ! PoisonPill will not be processed
    println("Sending Jonathan a PoisonPill ...")

    // we can look up actors by specifying the full path or relative path
    val jonathan = actorSystem.actorSelection("/user/Parent/Jonathan")
    jonathan ! PoisonPill
    println("jonathan was killed")

    Thread.sleep(5000)
    actorSystem.shutdown
}

// 13.6 graceful stop, killing an actor
// 13.8 monitoring the Death of an Actor with watch