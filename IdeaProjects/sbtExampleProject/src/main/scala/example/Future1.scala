package example

// the ExecutionContext imports a default thread pool
import scala.concurrent.ExecutionContext.Implicits.global
import scala.concurrent.Future
import scala.util.{Failure, Success}
import scala.util.Random

object Future1 extends App {

    println("starting calculation ...")
    // to create a Future, we pass it a block
    // of code we wish to run
    val f: Future[Int] = Future {
        Thread.sleep(Random.nextInt(100))
        42
    }

    println("before onComplete")
    // the .onComplete method sets up the callback;
    // because the Future is off running concurrently somewhere
    // we don't exactly know when the result will be computed
    // and returned. When a Future returns a result, a future
    // is said to be completed. It may either be successful and failed.
    // The return type is of type Unit, thus they can't be chained
    f.onComplete {
        case Success(value) => println(s"Got the callback, meaning = $value")
        case Failure(e) => e.printStackTrace
    }

    // do the rest of your work
    println("A ..."); Thread.sleep(100)
    println("B ..."); Thread.sleep(100)
    println("C ..."); Thread.sleep(100)
    println("D ..."); Thread.sleep(100)
    println("E ..."); Thread.sleep(100)
    println("F ..."); Thread.sleep(100)
}
