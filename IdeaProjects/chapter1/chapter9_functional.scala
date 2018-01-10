import com.sun.glass.ui.MenuItem.Callback

// function literals, also known as anonymous functions
// given a List, we can pass an anonymous function to the
// filter method to return only even numbers
val x = List.range(0, 10)

// the most explicit form of defining an anonymous function
// the => list transforms the parameter list on the left into
// a new result using the algorithm on the right hand side
val evens = x.filter((i: Int) => i % 2 == 0)

// the expression above can be simplified to
// the following due to the fact that Scala
// allows us to the use _ wildcard instead of
// a variable name when the parameter only appears
// once in our function
x.filter(_ % 2 == 0)


// we can pass function around like a variable
// double is now a function value
// and we can later invoke it like other normal methods
val double = (i: Int) => i * 2
double(3)

// we can also pass it to any method that takes
// a function as a parameter
val x1 = List.range(0, 3)
x1.map(double)

// we can declare function literals implicitly or explicitly
// implicitly: let Scala infer the return type
val add1 = (x: Int, y: Int) => x + y

// explicitly: declare the return type ourselves
val add2: (Int, Int) => Int = (x, y) => {
    x + y
}

// we can assign an existing function/method to a variable
// this is called a partially applied function, since cos
// requires one argument, which we have not supplied
val c = scala.math.cos(_)
c(0)


// we can define a method that takes a simple function
// as a method parameter;
// the callback: () portion defines a function that has
// no parameters, if it does, the type would be listed
// inside the parenthesis
// And the => Unit part indicates that this function returns nothing
// the Unit type is similar to void
def executeFunction(callback: () => Unit): Unit = {
    callback()
}
val sayHello = () => println("saying hello")
executeFunction(sayHello)

// the general syntax for having a function as a method parameter is:
// and the parenthesis is optional if the function only takes one argument
// parameterName: (parameterType) => returnType
// so to define a function that takes two Ints and returns a Boolean
// use the following function signature
// executeFunction(f: (Int, Int) => Boolean)
// here's a concrete three step process:

// 1. define the method
def exec(callback: (Any, Any) => Unit, x: Any, y: Any): Unit = {
    callback(x, y)
}

// 2. define a function or method to pass in
def printTwoThings(a: Any, b: Any): Unit = {
    println(a)
    println(b)
}

// 3. pass the function and the additional parameters
case class Person(name: String)
exec(printTwoThings, "Hello", Person("Dave"))


// using closures
// a closure begins with a function and a variable
// declared in the same scope, but separate from
// one another. When the function is executed at
// some other point, it magically is still aware
// of the variable it refers to
var votingAge = 18
val isOfVotingAge = (age: Int) => age >= votingAge
isOfVotingAge(20)

// we can see that the function and the field are still entangled
votingAge = 21
isOfVotingAge(20)


// using partially applied functions
// when we only supply the first two arguments, but not the third
val sum = (a: Int, b: Int, c: Int) => a + b + c
val f = sum(1, 2, _: Int)

// we later provide all the parameters needed to complete the function value
f(3)


// define a function that returns a function
// so on the right hand side of the = sign is our function literal
def saySomething(prefix: String) = (s: String) => {
    prefix + " " + s
}

// sayHi is now our anonymous function
val sayHi = saySomething("hi")
sayHi("Al")

// another example is that the function it returns can be based on
// the language specified
def greeting1(language: String) = (name: String) => {
    language match {
        case "english" => "Hello, " + name
        case "spanish" => "Buenos dias, " + name
    }
}

// in the code above, if it's not clear that greeting is returning a function
// we can make the code a bit more explicit
def greeting2(language: String) = (name: String) => {
    val english = () => "Hello, " + name
    val spanish = () => "Buenos dias, " + name
    language match {
        case "english" => english()  // remember the parenthesis
        case "spanish" => spanish()
    }
}
val hello = greeting2("english")
hello("Al")


// partial functions
// imagine a normal function that divides 1 number by another:
// (x: Int) => 42 / x
// as defined, this function blows up when the input parameter x is 0
// although we can use can use a try catch expression to handle this
// kind of situation, we can define a partial functions to tell Scala
// that the function will return answer for only a subset of all possible input
val divide = new PartialFunction[Int, Int] {
    def apply(x: Int) = 42 / x

    def isDefinedAt(x: Int): Boolean = x != 0
}
// with this approach, we can test the function prior to using it
if (divide.isDefinedAt(1)) divide(1)

// partial functions are often written using case statements
// the trait of the PartialFunction is defined as:
// trait PartialFunction[-A, +B] extends (A) => B
// the => part means it's transforming type A into type B
val divide2: PartialFunction[Int, Int] = {
    case d: Int if d != 0 => 42 / d
}
divide2.isDefinedAt(0)

// partial function also works with the collect method since
// it is written to test for the isDefinedAt method for each
// element it is given (if we were to use the map method this
// would give us an error)
List(0, 1, 2).collect(divide2)

// some other examples:
val convert1to5 = new PartialFunction[Int, String] {
    val nums = Array("one", "two", "three", "four", "five")

    def apply(i: Int) = nums(i - 1)

    def isDefinedAt(i: Int) = i > 0 && i < 6
}

val convert6to10 = new PartialFunction[Int, String] {
    val nums = Array("six", "seven", "eight", "nine", "ten")

    def apply(i: Int) = nums(i - 1)

    def isDefinedAt(i: Int) = i > 5 && i < 11
}
// the two functions above can only handle 5 numbers,
// but we can combine the two partial function using orElse
// and now they can handle 10
val sample = 1 to 5
val numbers = sample.map(convert1to5 orElse convert6to10)
