
import scala.io.Source
import java.io.{FileNotFoundException, IOException}

// open a plain text file and process the file line by line
// the getLines method returns an iterator that has each
// line without any newline character
val bufferedSource = Source.fromFile("example.txt")
for (line <- bufferedSource.getLines) {
    println(line.toUpperCase)
}
bufferedSource.close

// handle exception
val filename = "example.txt"
try {
    val buffered = Source.fromFile(filename)
    for (line <- buffered.getLines) {
        println(line)
    }
} catch {
    case e: FileNotFoundException => println(s"$filename not found")
    case e: IOException => println("IO error")
}


// https://alvinalexander.com/scala/how-to-use-duck-typing-in-scala-structural-types
// Scala duck typing or so called structural typing
// e.g. a method that requires its parameter has a speak method;
// in a statically typed language, this ensures that the input parameter
// has the speak method, or else the code won't compile.
// the <: symbol is used to define an upper bound. So in our
// example this is saying A must be a subtype of a type that has a speak method.
// Not recommended when performance is a concern
def speakMethod[A <: { def speak(): Unit }](obj: A): Unit = {
    obj.speak()
}
class Dog { def speak() { println("woof") } }
class Klingon { def speak() { println("Qapla!") } }
speakMethod(new Dog)
speakMethod(new Klingon)


// partial application, we can create this by calling
// the function with only one parameter followed by an
// underscore.
def add(a: Int)(b: Int) = a + b
val onePlusFive = add(1)(5)
val addFour = add(4)(_)
val twoPlusFour = addFour(2)
assert(onePlusFive == twoPlusFour)

// we could use any argument for the curried function,
// however, if it's not the first argument, we would need to specify the type
def curried(a: Int)(b: String) = { println(s"$a, $b") }
curried(1)(_)
curried(_: Int)("word")

// a "normal" add function is of the type (Int, Int) => Int,
// on the other hand, a "curried" add function would be of
// type Int => (Int => Int)
def curryBinaryOperator[A](operator: (A, A) => A): A => (A => A) = {
    def curry(a: A): A => A = {
        (b: A) => operator(a, b)
    }
    curry
}
def multiply(a: Int, b: Int) = a * b
val multiplyCurried = curryBinaryOperator(multiply)


// example of using this pattern to ensure resource is closed automatically
// when it goes out of scope
object Control {
    def using[A <: { def close(): Unit }, B](resource: A)(f: A => B): B = {
        try {
            f(resource)
        } finally {
            resource.close()
        }
    }
}
import Control._

def readTextFile(filename: String): Option[List[String]] = {
    try {
        val lines = using(Source.fromFile(filename)) { source =>
            (for (line <- source.getLines) yield line).toList
        }
        Some(lines)
    } catch {
        case e: Exception => None
    }
}

val filename1 = "example.txt"
readTextFile(filename1) match {
    case Some(lines) => lines.foreach(println)
    case None => println("couldn't read files")
}


// Scala doesn't offer any file writing capability
// so we fall back to using Java FileWriter
// note that if we have lots of small writes, we should
// consider BufferedWriter as it saves up small writes and
// writes in one large chunk
// https://beginnersbook.com/2014/01/how-to-write-to-file-in-java-using-bufferedwriter/
// https://stackoverflow.com/questions/30398924/what-is-the-best-way-to-write-and-append-a-large-file-in-java?noredirect=1&lq=1
import java.io.{File, FileWriter}
val mycontent = "This String would be written"
val file = new File("output.txt")
val filewriter = new FileWriter(file)
filewriter.write(mycontent)
filewriter.close


// process every character in a file
def countLines(source: Source): Long = {
    // new line's ascii code is 10
    // http://www.asciitable.com/
    val NEWLINE = 10
    var count = 0L
    for {
        // get each line, loop through each character
        // in each line and process each character
        line <- source.getLines
        c <- line
        if c.toByte == NEWLINE
    } count += 1
    count
}
val source = Source.fromFile("example.txt")
countLines(source)
source.close


// process a .csv file
import scala.collection.mutable.ArrayBuffer
val rows = ArrayBuffer[Array[String]]()
using(Source.fromFile("example.txt")) { source =>
    // if there's a header in the .csv file that
    // we wish to remove, we can add a drop(1)
    // after the .getLines
    for (line <- source.getLines) {
        rows += line.split(",").map(_.trim)
    }
}
rows


// serializing a Scala object
import java.io.{ObjectInputStream, FileInputStream}
import java.io.{ObjectOutputStream, FileOutputStream}

// add the annotation to the class to ensure compatibility
// https://stackoverflow.com/questions/285793/what-is-a-serialversionuid-and-why-should-i-use-it
@SerialVersionUID(123L)
class Stock(var symbol: String, var price: BigDecimal) extends Serializable {
    override def toString: String = f"$symbol%s is ${price.toDouble}%.2f"
}

val nflx = new Stock("NFLX", BigDecimal(85.00))

// write instance out to a file
val oos = new ObjectOutputStream(new FileOutputStream("nflx"))
oos.writeObject(nflx)
oos.close

// read the object back in
val ois = new ObjectInputStream(new FileInputStream("nflx"))
val stock = ois.readObject.asInstanceOf[Stock]
ois.close
println(stock)




// 12.1 Arm library, scala sbt
// 12.6 scalatest