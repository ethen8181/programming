// availability:
// 1. private makes the method accessable to the current class
// and other instances of the current class
// 2. protected makes the method available to the sub-class


// the syntax to invoke a method in an immediate parent class
// is the same as java. We use super to refer to the parent class
// and then provide the method name
class FourLeggedAnimal {
    def walk = { println("I'm walking") }
    def run = { println("I'm running") }
}

class Dog extends FourLeggedAnimal {
    def walkThenRun = {
        super.walk
        super.run
    }
}
val suka = new Dog
suka.walkThenRun


// defining a method that returns multiple items
// in Java we might need to define a one-off class,
// but in Scala we can return tuples
def getStockInfo = {
    // some other code here
    ("NFLX", 100.00, 101.00)
}

// and we can assign variable names when calling the method
// this is probably the most readable way
val (symbol, currentPrice, bidPrice) = getStockInfo

// or we can set a single variable equal to the tuple returned
// by the method, and access it later with tuple underscore syntax
val result = getStockInfo
println(result._1)  // note that index starts from 1
println(result._2)


// in Scala, the convention is to define the accessor
// without parenthesis after the method name, as the
// accessor should have no side effect
class Pizza {
    // calling crustSize with parenthesis would result in an error
    // and unlike Java, the convention in Scala is to leave off the get
    // so we do not need to write getCrustSize
    def crustSize = 12
}
val p1 = new Pizza
p1.crustSize


// creating variable that takes variable argument,
// we can define this in our method by adding a * character
// after the field type, given this declaration, the printAll
// method below can be called with zero or more parameters.
// Note that this varags field must be the last argument
def printAll(strings: String*): Unit = {
    // we typically use a loop to handle varargs argument
    strings.foreach(println)
}
printAll()
printAll("foo")
printAll("foo", "bar")

// use _* to adapt to sequence, we can think
// of it as the splat operator, it tells the compiler
// to pass each element of the sequence as an argument,
// as oppose to passing the sequence as a single argument
val fruits = List("apple", "banana", "orange")
printAll(fruits: _*)


// supports method chaining
class Person {
    protected var fname = ""
    protected var lname = ""

    // notice we return this as the returned object,
    // and the type becomes this.type. The this.type
    // return type ensures that when we extend this class
    // the method chaining will still work as expected
    def setFirstName(firstName: String): this.type = {
        fname = firstName
        this
    }

    def setLastName(lastName: String): this.type = {
        lname = lastName
        this
    }
}

class Employee extends Person {
    protected var role = ""

    def setRole(role: String): this.type = {
        this.role = role
        this
    }

    override def toString: String = {
        "%s %s %s".format(fname, lname, role)
    }
}
val employee = new Employee

// we can now perform method chaining, or so called fluent programming
employee.
setFirstName("Al").
setLastName("Alexander").
setRole("Developer")
println(employee)

// ? 5.2. trait