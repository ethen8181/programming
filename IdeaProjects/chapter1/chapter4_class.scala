
// in Scala, the primary constructor of a class
// consists of:
// - the constructor parameter
// - methods that are called within the body of the class
// - statements and expressions that are executed within the body of the class
class Person(var firstName: String, var lastName: String) {
    println("constructor begins")

    // declare some class fields
    var age = 0
    private val HOME = System.getProperty("user.home")

    // some methods
    override def toString: String = s"$firstName $lastName is $age years old"
    def printHome() { println(s"HOME = $HOME") }
    def printName() { println(this) }  // uses toString

    // when we call a method in the body of the class, that is also part of the constructor
    printHome
    printName
    println("still in constructor")
}
val p: Person = new Person("Adam", "Meyer")

// in our class, the two constructor arguments are declared as var fields,
// meaning they can be accessed and mutated (analogous to getters and setters)
p.age = 10
println(p.age)


// field visibility

// when fields are declared as var
// Scala generates both getters and setters
class Person1(var name: String)
val p1 = new Person1("Alex")
println(p1.name)
p1.name = "Bob"
println(p1.name)

// when a field is declared as val,
// the value can't be changed once it's set
// (like final in Java) thus it only has getters

// when neither val or var is declared, then the visibility
// of the field becomes very restricted as neither getter or
// setter is defined. This has the exception of case class,
// where its constructor parameters are val by default.
// This is a nice convenience due to the fact that it's
// often used in functional programming as immutable records
case class Person2(name: String)
val p2 = Person2("Ethen")  // notice there's no new when instantiating case class
println(p2.name)

// we can provide default values and use named arguments
class Socket(val timeout: Int = 1000, val linger: Int = 1000) {
    override def toString: String = s"timeout: $timeout, linger: $linger"
}
println(new Socket)
println(new Socket(timeout = 5000))

// overriding getters and setters, or so called accessors and mutators
// in Scala:
// the convention is to add a leading underscore to the constructor parameter
// so that it does not conflict with the accessor method; note that it's
// necessary to declare the variable as private to prevent Scala from
// generating its accessor and mutator
// then the name_= conforms to the Scala convention (underneath the hood,
// Scala will translate the = to $eq to work with the JVM)
class Person3(private var _name: String) {
    def name = _name  // accessor
    def name_=(aName: String) { _name = aName }  // mutator
}
val p3 = new Person3("Johnny")
p3.name = "newName"
println(p3.name)


// as discussed before, defining a field as private prevents
// getters and setters from automatically being generated.
class Stock {
    // if we set it to private[this], then the field becomes
    // object-private, which means isHigher will no longer work
    // as the field can't even be accessed by other instances
    private var price: Double = _
    def setPrice(p: Double) { price = p }
    def isHigher(that: Stock): Boolean = this.price > that.price
}
val s1 = new Stock
s1.setPrice(20)
val s2 = new Stock
s2.setPrice(100)
println(s2.isHigher(s1))


// we can initialize a field with a block of code or function;
// the "lazy" keyword will delay the initialization until it is
// access, which might be useful if it will take a long time to
// run, and we wish to defer that long process
class Foo {
    lazy val text = {
        var lines = ""
        try {
            lines = io.Source.fromFile("temp").getLines().mkString
        } catch {
            case e: Exception => lines = "error occurred"
        }
        lines
    }
}
val foo = new Foo


// setting uninitialized fields using Option instead of null
case class Address(city: String, state: String, zip: String)
case class Person4(var username: String = "", var password: String = "") {
    var age: Int = 0
    var address: Option[Address] = None
}
val p4 = Person4("alvinalexander", "secret")

// we can assign address with Some(Address())
p4.address = Some(Address("Talkeetna", "AZ", "99676"))

// to access the field we can use foreach, if the value
// is None, then it will be skipped
p4.address.foreach { a =>
    println(a.city)
    println(a.state)
    println(a.zip)
}


// handling constructor parameters when extending a class
// base class Person and a sub-class Employee
case class Address1(city: String, state: String)
class Person5(var name: String, var address: Address1) {
    override def toString: String = if (address == null) name else s"$name @ $address"
}

// because the base class's name and address field already has a getter and setter
// in the sub-class we leave out the var declaration
class Employee(name: String, address: Address1, var age: Int) extends Person5(name, address) {
}
val teresa = new Employee("Teresa", Address1("Louisville", "KY"), 25)
println(teresa.address)
println(teresa.age)


// call a super class constructor
class Animal(var name: String, var age: Int) {

    // auxiliary constructor
    def this(name: String) {
        // first line of the auxiliary constructor
        // must be a call to another constructor of the current class
        this(name, 0)
    }

    override def toString: String = s"$name is $age years old"
}

// calls the Animal one-argument constructor
// we can instead call the two-argument constructor
// by extends Animal(name, 0)
class Dog(name: String) extends Animal(name) {

}


// if trait is more flexible than an abstract class,
// (a class can only extend one abstract class)
// but we can still use an abstract class when the
// base class needs to have a constructor
abstract class Pet(var name: String) {
    // to declare the method as abstract,
    // leave the method undefined, there is no need
    // for the keyword abstract
    def speak

    // abstract field
    val greeting: String
    var age: Int
}


// case class is often used in match expression.
// it also generates a lot of boilerplate code for you, including:
// 1. an apply method so we don't need to use the new keyword to
// create a new instance of the class
// 2. a good toString method
// 3. field are val by default, thus getters are generated for them
// 4. an unapply method is generated, making it easy to perform
// pattern matching
// 5. equals, hashCode, copy method are generated
// thus if we don't all these boilerplate code, we should define
// a regular class and implement the functionality ourselves
case class Person6(name: String, relation: String)
val emily = Person6("Emily", "niece")
emily match { case Person6(n, r) => s"$n $r" }

val hannah = Person6("Hannah", "niece")
println(hannah == emily)

val emily2 = emily.copy()
println(emily2)


// object equality, like Java we define the equals and hashCode method,
// but instead of using equals method to compare two instances, we use
// the == operator, which calls the equals method under the covers
class Person7(name: String, age: Int) {
    def canEqual(a: Any): Boolean = a.isInstanceOf[Person7]

    override def equals(that: Any): Boolean = that match {
        case that: Person7 => that.canEqual(this) && this.hashCode == that.hashCode
        case _ => false
    }

    override def hashCode: Int = {
        val prime = 31
        var result = 1
        result = prime * result + age
        result = prime * result + (if (name == null) 0 else name.hashCode)
        return result
    }
}

// ? 4.3 auxiliary constructor
// ? 4.4 private primary constructor, utility class
// ? how to write equality in Java
// http://www.artima.com/lejava/articles/equality.html
// ? scalaTest
