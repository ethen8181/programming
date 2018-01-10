

// looping through collections:
val arr = Array("banana", "apple", "orange")

// write multiple lines in a block
for (element <- arr) {
    // some other stuff
    val s = element.toUpperCase
    println(s)
}

// return something to create a new collection with yield
val newArr = for (element <- arr) yield {
    // some other stuff
    val s = element.toUpperCase
    s
}

// for loop counters
for ((element, counter) <- arr.zipWithIndex) {
    println(s"$counter is $element")
}

// ranges create with the <- symbol are called generators
// guards (if statements in for loops)
for (i <- 1 to 10 if i < 4) println(i)

// iterating over key and value of a Map
val names = Map("fname" -> "Robert", "lname" -> "Goren")
for ((key, value) <- names) {
    println(s"$key: $value")
}


// multiple for loops:
// print each element of a two dimensional array
val array = Array.ofDim[Int](2, 2)
for {
    i <- 0 to 1
    j <- 0 to 1
} println(s"($i)($j) = ${array(i)(j)}")

// consider using map instead of the for yield for comprehension
var fruits = scala.collection.mutable.ArrayBuffer[String]()
fruits += "apple"
fruits += "banana"
fruits += "orange"

val output1 = for (fruit <- fruits) yield fruit.toUpperCase
val output2 = fruits.map(fruit => fruit.toUpperCase)
println(output2)

// the break and continue functionality are offered within this package
import scala.util.control.Breaks
import scala.util.control.Breaks._

breakable {
    for (i <- 1 to 10) {
        println(i)
        if (i > 4) {
            break
        }
    }
}

// or we can do a labeled break
val Exit = new Breaks
Exit.breakable {
    for (j <- 'a' to 'z') {
        if (j == 'c') Exit.break else println(j)
    }
}

// tail recursion
// http://chrispenner.ca/posts/python-tail-recursion
// https://stackoverflow.com/questions/33923/what-is-tail-recursion
import scala.annotation.tailrec

def factorial(n: Int): Int = {
    @tailrec def factorialAcc(acc: Int, n: Int): Int = {
        if (n < 1) acc
        else factorialAcc(n * acc, n - 1)
    }
    factorialAcc(1, n)
}


// counting the number of 'p's in a string using the count method
val searchMe = "peter piper picked a peck of pickled peppers"
val numPs = searchMe.count(_ == 'p')

// if else ternary operator
def max(a: Int, b: Int) = if (a > b) a else b
def abs(a: Int) = if (a > 0) a else -a

// using match statement like switch statement;
// in this scenario, we could even use a Map data structure
val i = 1
val result = i match {
    case 1 => "One"
    case 2 => "Two"
    // match all others with a wildcard,
    // or if we can give it a variable name call default
    // (can be any other variable name, but default is
    // arguably more readable
    case _ => "Other"
}

// different types of pattern we can match
case class Dog(name: String)

def echoWhatYouGaveMe(x: Any): String = x match {
    // constant pattern
    case 0 => "zero"
    case true => "true"
    case "hello" => "You said 'hello'"
    case Nil => "an empty list"

    // sequence patterns
    // _* stands for zero or more elements
    case List(0, _, _) => "a three element list with 0 as the first element"
    case List(0, _*) => "a list beginning with 0, having any number of elements"

    // tuple pattern
    case (a, b) => s"got $a, $b"

    // constructor patterns
    case Dog("suka") => "found a dog named Suka"

    // typed pattern
    case s: String => s"you gave me this string: $s"
    case i: Float => s"Thanks for the float: $i"
    case arr: Array[Int] => s"An array of int: ${arr.mkString(",")}"
    case d: Dog => s"dog: ${d.name}"
    case m: Map[_, _] => m.toString

    // default wildcard
    case _ => "Unknown"
}

// adding variables to pattern
// the general syntax is variableName @ pattern:
// the problem this solves is this:
// case list: List(1, _*)
// the code above will not work
def matchType(x: Any): String = x match {
    // case Some(x) => s"$x"  // returns x,
    case x @ Some(_) => s"$x"  // returns Some(x)
}
println(matchType(Some("foo")))

// using if statement after case
def speak(d: Dog) = d match {
    case Dog(name) if name == "Oreo" => println("Hi")
    case Dog(name) if name == "Olly" => println("Hello")
    case _ => println("default case")
}
speak(new Dog("Oreo"))

// use match as oppose to if else isInstanceOf
// when the checking becomes more complex


// equivalent way of creating an immutable list
val x = List(1, 2, 3)
val y = 1 :: 2 :: 3 :: Nil

// take advantage of the fact that the last element is a Nil
// to write a recursive algorithm
def listToString(list: List[String]): String = list match {
    // explanation for ::
    // When seen as a pattern, an infix operation such as `p op q` is equivalent to `op(p, q)`. That is,
    // the infix operator op is treated as a constructor pattern. In particular, a cons pattern such as x :: xs
    // is treated as ::(x, xs). This hints that there should be a class named :: that correspond to the
    // pattern constructor.
    // https://stackoverflow.com/questions/1022218/scala-match-decomposition-on-infix-operator
    // https://stackoverflow.com/questions/8665580/scala-match-case-using-for-lists?rq=1
    case s :: rest => s + " " + listToString(rest)
    case Nil => ""
}
val fruit = List("apple", "orange", "banana")
listToString(fruit)

// scala's try catch's syntax is similar to Java, except the
// the catch uses match expression
val s = "Foo"
try {
    val i = s.toInt
} catch {
    // we can add multiple exception types
    case e: NumberFormatException => e.printStackTrace()
}


try {
    val i = s.toInt
} catch {
    // if we don't really care about which specific exception
    // might be thrown, we can catch them all and maybe output it to a log
    case e: Throwable => e.printStackTrace()
}
