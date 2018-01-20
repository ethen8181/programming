

// 14.8 generating scaladoc
// https://docs.scala-lang.org/style/scaladoc.html

/**
  * A class to represent a human being.
  *
  * (Further documentation): Specify the `name`, `age`, and `weight` when creating
  * a new `Person`
  * {{{
  * val p = Person("Al", 42, 200.0)
  * p.name
  * p.age
  * p.weight
  * }}}
  *
  * @constructor Create a new person with a `name`, `age`, and `weight`.
  * @param name The person's name
  * @param age The person's age
  * @param weight The person's weight
  *
  */
class Person(var name: String, var age: Int, var weight: Double) {

    /**
      * @constructor This is an auxiliary constructor. Just need a `name` here.
      */
    def this(name: String) {
        this(name, 0, 0.0)
    }

    /**
      * @return Returns a greeting based on the `name` field
      */
    def greet = s"Hello, my name is $name"
}
