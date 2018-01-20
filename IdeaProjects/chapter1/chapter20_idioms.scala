
// ?? Twitter's effective Scala
// http://bit.ly/1c3BpjS
// ?? Scala style guide
// http://docs.scala-lang.org/style/

// 20.1 writing pure functions
// The function always evaluate to the same result. It
// will not depend on any hidden state or value nor will
// it mutate the argument its given

// reach for immutable collection and immutable variables, i.e. val
// first before reaching for the mutable ones
import java.io.FileNotFoundException

import scala.collection.mutable.ArrayBuffer

def evilMutator(people: ArrayBuffer[Int]) {
    // even though the input variable to the method
    // is marked with val, we can still modify the
    // content because ArrayBuffer is mutable
    people.clear()
}
val people = ArrayBuffer(1, 2, 3)
evilMutator(people)
people.foreach(println)


// some developers prefers the following combination:
// declare a mutable collection as val, and it is typically
// made private to its class or method
// declare an immutable collection as var and it is made to
// be publicly visible
class Pizza {
    // _toppings is created as ArrayBuffer since we know
    // it will be added and removed frequently.
    // it is declared as val because it will never be reassigned.
    // it is marked as private so its accessor will not be visible
    // outside of the class
    private val _toppings = ArrayBuffer[Int]()

    // we return an immutable collection whenever the end-user tries
    // to access the toppings
    def toppings = _toppings.toList

    // other people can manipulate the collection
    def addTopping(t: Int) = { _toppings += t }
    def removeTopping(t: Int) = { _toppings -= t }
}


// express oriented programming
// statements do not return results and are executed solely
// for their side effects: e.g.
// order.calculateTaxes()
// while expressions always returns a result and often do not
// have side effect at all
// val tax = calculateTax(order)


// match expression
// can be used to replace the switch statement
val i = 1
val month = i match {
    case 1  => "January"
    case 2  => "February"

    // more months here ...

    case 11 => "November"
    case 12 => "December"
    case _  => "Invalid month"  // the default, catch-all
}

// can be used to replace unwieldy if then statement
i match {
    case 1 | 3 | 5 | 7 | 9 => println("odd")
    case 2 | 4 | 6 | 8 | 10 => println("even")
}

// try-catch syntax
import java.io.IOException
import scala.io.Source

def readTextFile(filename: String): Option[List[String]] = {
    // there's also the try/success/failure approach as oppose
    // to the Option/Some/None approach
    try {
        Some(Source.fromFile(filename).getLines.toList)
    } catch {
        case ioe: IOException => None
        case fnf: FileNotFoundException => None
    }
}

// as a body of a function or method
def isTrue(a: Any) = a match {
    case 0 | "" => false
    case _ => true
}


// Ban nulls from any of your code. Period.
// When a field doesn't have a initial default value
// initialize it with Option instead of null.
// When a method doesn't produce the intended result,
// we may be attempted to return null, use an Option or Try instead
case class Address(city: String, state: String, zip: String)

class User(email: String, password: String) {
    // do not declare field as null,
    // and can cause problems in our application
    // if they're not assigned before they are accessed
    // var firstName: String = _
    var firstName: Option[String] = None
    var lastName: Option[String] = None
    var address: Option[Address] = None
}

// we can create the user and assign other fields like the following
val u = new User("al@example.com", "secret")
u.firstName = Some("Al")
u.lastName = Some("Alexander")
u.address = Some(Address("Talkeetna", "AK", "99676"))

u.firstName.getOrElse("<not assigned>")
u.address.foreach { a =>
    // Option can be thought of as a collection with zero or one
    // elements, thus if address was not assigned the foreach loop
    // won't be executed
    println(a.city)
    println(a.state)
    println(a.zip)
}

// on a related note, we should use an Option in a constructor
// if a field is optional
case class Stock(id: Long,
                 var symbol: String,
                 var company: Option[String])

// converting legacy code that returns null to Option
def getName: Option[String] = {
    var name: String = _
    if (name == null) None else Some(name)
}

// returning an Option from a method
def toInt(s: String): Option[Int] = {
    try {
        Some(Integer.parseInt(s))
    } catch {
        case e: Exception => None
    }
}
// it returns Some if it succeed and None if it fails
val x1 = toInt("1")
val x2 = toInt("foo")

// there're several ways to access the result
// getOrElse, foreach and a match expression
toInt("1").getOrElse(0)
toInt("1") match {
    case Some(i) => println(i)
    case None => println("That didn't work")
}

// using Option with Scala collection
// ways to eliminate Some and None
val bag = List("1", "2", "foo", "3", "bar")
bag.map(toInt).flatten
bag.flatMap(toInt)

// collect is another way to achieve the same result
bag.map(toInt).collect{ case Some(i) => i }


// try/sucess/failure
import scala.util.{Try, Success, Failure}

// this methods returns a successful result as long as
// y is not 0. When y is 0, an ArithmeticException
// happens, however, the exception isn't thrown out
// of the method, it is caught by Try and a Failure
// object is returned from the method.
// The weakness of Option is that it doesn't tell you
// why something failed, we just get a None instead of Some.
// If we need to know why it failed, use Try instead
def divideXByY(x: Int, y: Int) = {
    Try(x / y)
}
divideXByY(1, 1)
divideXByY(1, 0)
divideXByY(1, 1) match {
    case Success(i) => println(s"Success, value is: $i")
    case Failure(s) => println(s"Failed, message is: $s")
}

// the Try class has the added benefit that we can chain operations
// together, catching exceptions as we go
val x = "1"
val y = "2"
val z = for {
    a <- Try(x.toInt)
    b <- Try(y.toInt)
} yield a * b
val answer = z.getOrElse(0) * 2
