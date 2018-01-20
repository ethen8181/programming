import com.sun.crypto.provider.AESCipher.AES128_CBC_NoPadding
// Scala uses a collection of symbols to express different generic types
// including variance, bounds and constraints
// variance: defines the rules by which types can be passed into methods

class Grandparent
class Parent extends Grandparent
class Child extends Parent

class InvariantClass[A]
class CovariantClass[+A]
class ContravariantClass[-A]

def invarMethod(x: InvariantClass[Parent]) {}
def covarMethod(x: CovariantClass[Parent]) {}
def contraMethod(x: ContravariantClass[Parent]) {}

// invarMethod(new InvariantClass[Child])          // ERROR - won't compile
invarMethod(new InvariantClass[Parent])            // success
// invarMethod(new InvariantClass[Grandparent])    // ERROR - won't compile

covarMethod(new CovariantClass[Child])             // success
covarMethod(new CovariantClass[Parent])            // success
// covarMethod(new CovariantClass[Grandparent])    // ERROR - won't compile

// contraMethod(new ContravariantClass[Child])     // ERROR - won't compile
contraMethod(new ContravariantClass[Parent])       // success
contraMethod(new ContravariantClass[Grandparent])  // success


// create class that uses generic types
class LinkedList[A] {
    private class Node[A](elem: A) {
        var next: Node[A] = _

        override def toString: String = elem.toString
    }

    private var head: Node[A] = _

    def add(elem: A): Unit = {
        // prepend to the list
        val node = new Node(elem)
        node.next = head
        head = node
    }

    private def printNodes(n: Node[A]): Unit = {
        if (n != null) {
            println(n)
            printNodes(n.next)
        }
    }

    def printAll() { printNodes(head) }
}

val ints = new LinkedList[Int]()
ints.add(1)
ints.add(2)
ints.printAll()

val strings = new LinkedList[String]()
strings.add("Nacho")
strings.add("Libre")
strings.printAll()

// when using generic types, the container can take subtypes
// of the base type we've specify in our code
class Dog { override def toString = "Dog" }
class SuperDog extends Dog { override def toString = "SuperDog" }
class FunnyDog extends Dog { override def toString = "FunnyDog" }

val dogs = new LinkedList[Dog]
val fido = new Dog
val wonderDog = new SuperDog
val scooby = new FunnyDog

dogs.add(fido)
dogs.add(wonderDog)
dogs.add(scooby)
dogs.printAll()


// pass a generic collection to a method that doesn't attempt to
// mutate the collection
def randomElement[A](seq: Seq[A]): A = {
    val randomNum = util.Random.nextInt(seq.length)
    seq(randomNum)
}
randomElement(Seq("Aleka", "Christina", "Tyler", "Molly"))
randomElement(List(1, 2, 3))


// the elements of Array, ArrayBuffer and ListBuffer can be mutated
// and they're all defined with invariant type parameters
// e.g. ArrayBuffer[A]
// conversely, collection that are immutable defines their generic
// type with the +A symbol
// e.g. Vector[+A]
// because their elements are immutable, adding this symbol makes
// them more flexible.
trait Animal {
    def speak
}

class Dog1(var name: String) extends Animal {
    def speak { println("Dog says woof") }
}

class SuperDog1(name: String) extends Dog1(name) {
    override def speak { println("I'm a SuperDog") }
}

// because Seq is immutable and defined with a covariant parameter type
// makeDogsSpeak accepts collection of both Dog1 and SuperDog1. This
// wouldn't be a problem for immutable class as we wouldn't be able
// to modify the input collection's element inside the method
def makeDogsSpeak(dogs: Seq[Dog1]) {
    dogs.foreach(_.speak)
}
val superDogs = Seq(new SuperDog1("Wonder Dog"), new SuperDog1("Scooby"))
makeDogsSpeak(superDogs)


// create a collection whose elements are all of the same base type
import collection.mutable.ArrayBuffer

trait CrewMember
trait Captain
trait FirstOfficer
trait ShipsDoctor
trait StarfleetTrained
class Officer extends CrewMember
class RedShirt extends CrewMember

val kirk = new Officer with Captain
val spock = new Officer with FirstOfficer
val bones = new Officer with ShipsDoctor

// this states that any instance of Crew can only
// have elements that are of type CrewMember
class Crew[A <: CrewMember] extends ArrayBuffer[A]

// in addition to creating a collection of officers
// we can also create a collection of RedShirt since
// they both extend CrewMember
// val redshirts = new Crew[RedShirt]()
val officers = new Crew[Officer]()
officers += kirk
officers += spock
officers += bones

// 19.7., 19.8 Selectively Adding New Behavior to a Closed Model
