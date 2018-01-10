
// trait is like an interface in Java
// we can declare the methods in our trait
// that we want extending classes to implement;
// for example, we could declare a logging trait
// and make it available to other types when debugging
trait BaseSoundPlayer {

    // if the method doesn't take any argument,
    // then we only need to declare the name.
    // On the other hand, if it does require parameters
    // then list them as usual
    def play
    def close
    def pause
    def stop
    def resume

    // trait can also provide method implementation
    def start { println("start") }
}

// when a class extends a trait, it must implement
// all the methods unless it's also an abstract class.
// for the first trait use the extends keyword and for
// subsequent trait, use the with keyword
class MP3SoundPlayer extends BaseSoundPlayer {
    def play = { println("play") }
    def close = { println("close") }
    def pause = { println("pause") }
    def stop = { println("stop") }
    def resume = { println("resume") }
}
val mp3 = new MP3SoundPlayer
mp3.play
mp3.start


// abstract of concrete fields in trait
// define an initial value to make the field concrete;
// otherwise, don't assign an initial value to make it abstract
trait PizzaTrait {
    var numToppings: Int  // abstract
    var size: Int = 14  // concrete
    val maxNumToppings: Int = 10  // concrete
}

class Pizza extends PizzaTrait {
    // override keyword is not necessary to override var field
    var numToppings: Int = 0  // override keyword is not needed
    size = 16  // override and var keyword are both not needed
    override val maxNumToppings: Int = 10  // override is required for val
}


// although Scala has abstract class, it's more common to use trait instead of
// abstract class to implement base behavior as a class can only extend one
// abstract class, whereas a class can implement multiple traits
trait Pet {
    def speak { println("Yo") }
}

class Cat extends Pet {
    // we can now override the speak method,
    // or leave it as is
    override def speak = { println("meow") }
}
val cat = new Cat
cat.speak


// marking traits so that they can only be used by a certain type
class StarShip

trait StarShipWarpCore {
    // begin our trait with a this: Type => declaration
    // this ensures any class that mix-in the trait must
    // ensure its type conforms to the trait's self type
    this: StarShip =>

    // we can also require that any type that wishes to
    // extend it must extend multiple other types. e.g.
    // this: StarShip with WarCoreEjector =>
}

class Enterprise extends StarShip with StarShipWarpCore

// this won't compile
// class RomulanShip
// class Warbird extends RomulanShip with StarShipWarpCore


// we can also ensure a trait can only be added to a type
// that has a specific method. This approach is known as
// structural type because we are limiting what classes
// the trait can be mixed into by stating the class must
// have a certain structure
trait WarpCore {
    this: {
        def ejectWarpCore(password: String): Boolean
        def startWarpCore: Unit
    } =>
}

class Enterprise1 extends WarpCore {
    def ejectWarpCore(password: String): Boolean = {
        if (password == "password") {
            println("core ejected")
            true
        } else {
            false
        }
    }

  def startWarpCore: Unit = {
      println("starting")
  }
}
val enterprise1 = new Enterprise1
enterprise1.startWarpCore
