// strings

// declare a variable or concatenate a string
val s1 = "Hello World"
val s2 = "Hello" + "World"
println(s1.length)

// scala string has both string and collection features
// e.g. drop the first two letters, take the first two letters and capitalize them
println("scala".drop(2).take(2).capitalize)

// in Scala, we test object equality using the == operator
// compare two strings in case-insensitive manner by converting cases
val s3 = "Hello"
val s4 = "hello"
println(s3.toUpperCase == s4.toUpperCase)

// compare while ignoring cases
println(s3.equalsIgnoreCase(s4))

val foo =
  """This is
    |a multiline
    |String
  """.stripMargin
println(foo)

// string splitting
val s5 = "eggs, milk, butter, Coco Puffs"
s5.split(",").map(_.trim)

// string interpolation:
// e.g. precede the string with the letter s and include
// each variable inside the string, with a $ preceded in front
val name = "Fred"
val age = 33
val weight = 200.0
println(s"$name is $age year old, and weighs $weight pounds")

// we can use expressions in string interpolation by surrounding them with brackets
println(s"Age next year: ${age + 1}")

// there's also the .format method similar to python
val s6 = "%s is %s year old, and weighs $.0f pounds".format(name, age, weight)
println(s6)

// processing one character at a time
val upper1 = "hello, world".map(c => c.toUpper)
println(upper1)

// we can shorten the syntax to replace the each individual element with an underscore
val upper2 = "hello, world".map(_.toUpper)
println(upper2)

// for loop base solution
val upper3 = for (c <- "hello world") yield c.toUpper
println(upper3)

// chaining methods
val result1 = "hello, world".filter(_ != 'l').map(_.toUpper)
println(result1)

val result2 = for {
    c <- "hello world"
    if c != 'l'
} yield c.toUpper
println(result2)

// whereas map and for are used for transforming one collection into another,
// foreach method is typically used to operate on each element without returning a result,
// the best example being println
"hello".foreach(println)

// create a regex by invoking the .r method of a String
// after that we can use findAllIn or findFirstIn to search for
// all the matches for the first match
val numPattern = "[0-9]+".r
val address = "123 Main Street Suite 101"

// returns a none empty iterator if there's a match
val matches1 = numPattern.findAllIn(address)
matches1.foreach(println)
val matches2 = matches1.toArray

// it returns an Option/Some/None pattern, it
// holds zero or one value, so a method defined to return
// Option[String] will either return Some(String) or None;
// we can use the .getOrElse method to return a default value
// if the method could not find any match
val match3 = numPattern.findFirstIn(address).getOrElse("no match")
println(match3)

// replacing patterns in string
val address1 = address.replaceAll("[0-9]", "x")

// extract parts of a string that matches pattern:
// place parentheses around the regex patterns,
// the code below will extract the numeric field
// and the alphabetic field from the given strings
// as two separate variables, count and fruit
val pattern = "([0-9]+) ([A-Za-z]+)".r
val pattern(count, fruit) = "100 Banana"

// to access a character from a string,
// we can use the Java .charAt method or
// use to preferred Scala Array indexing
"hello".charAt(0)

// this is actually a method call,
// behind the scenes it gets translated to
// a .apply method
"hello"(0)
"hello".apply(0)

// we can add behavior to classes by writing implicit conversions
// e.g. extending Strings, notice that apart from the implicit
// keyword, everything else remains the same. In real world, we will
// need to wrap this inside an object
implicit class StringImprovements(val s: String) {
    def increment: String = s.map(c => (c + 1).toChar)
    def decrement: String = s.map(c => (c - 1).toChar)
    def hideAll: String = s.replaceAll(".", "*")
    def asBoolean: Boolean = s match {
        case "0" | "zero" | "" | " " => false
        case _ => true
    }
}

// notice that we to not need to declare it as the
// StringImprovements class, we can declare it as String
// and when it can can't find the method from the String
// class, it will start looking for the implicit class
"hello".increment
"0".asBoolean
