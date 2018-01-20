
// Short is a 16-bit signed value;
// we can access the primitive type's MinValue and MaxValue
Short.MinValue

// for working with datetime, the Java project Joda Time is
// popular and the Scala wrapper nscala-time

// we can convert String to numeric types using the to* method
"100".toFloat

// to perform calculation using bases other than 10, we can use
// the parseInt method from the Java Integer class
Integer.parseInt("1", 2)

// we can declare that our method may throw an exception
// by marking it with an throws annotation
@throws(classOf[NumberFormatException])
def toInt1(s: String) = s.toInt

// in Scala, situations like this are often times handled
// with the Option/Some/None pattern
def toInt(s: String): Option[Int] = {
    try {
        Some(s.toInt)
    } catch {
        case e: NumberFormatException => None
    }
}

val x = toInt("a").getOrElse(0)
val result = toInt("100") match {
    case Some(x) => x
    case None => 0  // however we wish to handle this
}


// declaring numeric types
val a1 = 1f
val a2 = 1d
val a3 = 1L

// replacements for the ++ and -- operators;
// note that we need to declare the variable
// as var to say that its value is changeable
var value = 1
value += 1
println(value)

// comparing floating point numbers
// as in Java and many other programming languages
// we solve this problem by declaring a method and
// specify the precision for our comparison;
// we can also name the method approximatelyEqual or
// EqualWithTolerance or some other name
def ~=(x: Double, y: Double, precision: Double): Boolean = {
    if ((x - y).abs < precision) true else false
}
val num1 = 0.3
val num2 = 0.1 + 0.2
~=(num1, num2, precision = 0.001)

// to handle very large numbers, use BigInt or BigDecimal
var largeNumber = BigDecimal(12345.678)

// check if they can be converted to other numeric types
// before actually converting them
if (largeNumber.isValidInt) largeNumber.toInt

// generating random numbers:
// setting the seeds and calling the
// .nextInt method with a cap on the
// randomly generated integer
val r = new scala.util.Random(100)
r.nextInt(100)

// create a sequence of known length but random numbers
for (i <- 1 to 5) yield r.nextInt(100)

// create ranges using until and to;
// until is exclusive while to is inclusive
for (i <- 1 to 5) println(i)
for (i <- 1 until 5) println(i)

// create the range and convert to array
val arr1 = (1 to 5).toArray
