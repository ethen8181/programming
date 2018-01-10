
// when an API requires us to pass in a class, in Java
// we would call .class on an object in Java
// in Scala we would instead use the classOf syntax
// e.g. accessing the methods of String class
val stringClass = classOf[String]
stringClass.getMethods

// when we wish to learn about the types Scala is automatically
// assigning on our behalf, we can call the getClass method
def printAll(numbers: Int*): Unit = {
    println("class: " + numbers.getClass)
}
printAll()
printAll(1, 2, 3)

// printing the class for debugging purpose
def printClass(x: Any): Unit = {
    println(x.getClass)
}
printClass(1)


// launching an application with an object
// the first way is to define an object that extends
// the App trait.

// the following is a simple but complete application
// we can compile this using scalac filename.scala
// and run the program using scala Hello
object Hello extends App {
    // when using this approach any command line arguments
    // to our application are already available through
    // the args object (Array[String]), which comes from the App trait
    if (args.length == 1) {
        println(s"Hello ${args(0)}")
    } else {
        println("Sorry, I didn't get your name")
    }
}

// the second approach is to define a main method in a manner
// similar to Java
object Hello2 {
    def main(args: Array[String]): Unit = {
        println("Hello")
    }
}


// we can create a singleton object to ensure that
// only one instance of a class exist, similar to
// static methods in Java
object CashRegister {
    def open { println("opened") }
    def close { println("closed") }
}

CashRegister.open
CashRegister.close

// this pattern is also common when creating utility functions
import java.util.Calendar
import java.text.SimpleDateFormat

object DateUtils {
    def getCurrentDate: String = getCurrentDateTime("EEEE, MM d")

    def getCurrentTime: String = getCurrentDateTime("K:m aa")

    private def getCurrentDateTime(dateTimeFormat: String): String = {
        val dateFormat = new SimpleDateFormat(dateTimeFormat)
        val calender = Calendar.getInstance
        dateFormat.format(calender.getTime)
    }
}
DateUtils.getCurrentTime


// creating static methods members with companion object
// we wish to create a class that has instance methods and static methods
// but in Scala, there is no static keyword. To achieve this, we need to
// create a companion object
class Pizza(var crustType: String) {
    override def toString: String = "crust type is " + crustType
}

// the companion object defined in the same file as the class
// and all static methods will go inside this object
object Pizza {
    val CRUST_TYPE_THIN = "thin"
    val CRUST_TYPE_THICK = "thick"
}
// members of the Pizza object can be accessed directly
// without needing to create a Pizza instance
println(Pizza.CRUST_TYPE_THIN)

// or we can create a new Pizza class,
// a side note is that a class and its corresponding
// companion object can access each other's private members
val p1 = new Pizza(Pizza.CRUST_TYPE_THICK)
println(p1)


// Scala code looks nicer when we don't have to use the new keyword
// to create new instances of a class.
// the first approach to do this is to define a companion object
// and define the apply method in the companion object with the desired constructor
class Person {
    var name: String = ""
    var age: Int = 0
}

object Person {
    // we can define different constructor
    def apply(name: String): Person = {
        val p = new Person
        p.name = name
        p
    }

    def apply(name: String, age: Int): Person = {
        val p = new Person
        p.name = name
        p.age = age
        p
    }
}

// underneath the hood our Person("Dawn") code
// is being translated into Person.apply("Dawn")
val dawn = Person("Dawn")
val arr = Array(Person("Dan"), Person("Elijah"))

// the other approach is to declare our class as a case class
// this works because it automatically generates a companion object
// with the apply method (also much more)

// ? 6.7 package object
// ? 6.9 factory method