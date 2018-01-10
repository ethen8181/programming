
// we can specify the type that we want for the collection
val x = List[Double](1, 100.0, 1000d)

// when we create an immutable collection such as vector, it may seem like
// we can add elements to it;
// what's actually happening is that it's pointing to a new collection every single
// during each time
// so attempting to modify one of its element would result in an error
// sisters(0) = "Molly"
var sisters = Vector("Melinda")
sisters = sisters :+ "Melissa"
sisters.foreach(println)

// variables declared as var can be reassigned to point at new data
// whereas val is like a final variable in Java, it can't be reassigned;
// and elements in a mutable collection can be changed, on the other hand
// element in an immutable collection can't be changed

// Vector is our go-to immutable sequence collection, i.e. if
// we wish to access elements efficiently by index
val v1 = Vector(1, 2, 3)
v1(0)

// we can't modify a vector, so we add an element to an existing vector
val v2 = v1 ++ Vector(4, 5, 6)

// we can use updated method to replace one element
val v3 = v2.updated(0, 10)

// we can use all the filtering methods to extract the elements we want
// out of the element and reassign to to a new collection
v1.take(2)
v1.filter(_ > 2)

// when we create a IndexedSeq, it returns a Vector,
// some people create this to be more generic
val v4 = IndexedSeq(1, 2, 3)


// ArrayBuffer is the go-to mutable indexed sequential collection
import scala.collection.mutable.ArrayBuffer
var nums = ArrayBuffer[Int](1, 2, 3)

// we can add one element
// add multiple elements
// or add elements from another collection
nums += 4
nums += (5, 6)
nums ++= List(7, 8)


// foreach method takes on parameter of the same type as the element
// in the collection and returns nothing (Unit)
val longWords = new StringBuilder
"Hello World it's AI".split(" ").foreach { e =>
    if (e.length > 4) {
        longWords.append(s" $e")
    } else {
        println("Not added: " + e)
    }
}
longWords

// in addition to using the foreach method on sequential collections
// it's also available on the Map class, it's implementation passes
// two parameters to our function
val m = Map("fname" -> "Tyler", "lname" -> "LeDude")
m.foreach(x => println(s"${x._1} -> ${x._2}"))
m.foreach{ case(key, value) => println(s"$key: $value") }


// we can loop over any traversable type using a for loop
val fruits = Traversable("apple", "banana", "orange")
for (f <- fruits) println(f.toUpperCase)

// if we need to loop over something N times, a Range works well
for (i <- 1 to 3) println(i)
for (i <- 0 until fruits.size) println(i)


// if we wish to loop over a sequential collection and would like
// to access the counter. We can use the zipWithIndex to build
// the counter. And because Scala's zipWithIndex generates a new
// sequence from the existing sequence, we can use .view of the
// tuple elements won't be created until they are needed
val days = Array("Sunday", "Monday", "Tuesday")
days.view.zipWithIndex.foreach {
    // the case statement matches the Tuple2
    case(day, count) => println(s"$count is $day")
}

// when using zipWithIndex the counter always starts at 0
// we can use the zip with Stream method to control the counter;
// Stream behaves similar to a List, except its element are
// computed lazily
days.zip(Stream from 1).foreach {
    // the case statement matches the Tuple2
    case(day, count) => println(s"$count is $day")
}


// we can transform one collection to another using the map method
// since unlike the for/yield approach, we can chain methods together
val s = " eggs, milk,  butter, Coco Puffs "
val items = s.split(",").map(_.trim)

// after adding a guard, a for/yield loop is no longer equivalent
// to a map call; if we wish to add a if statement, we should call
// filter and then map
val fruits1 = List("apple", "banana", "lime", "orange", "raspberry")
fruits1.filter(_.length < 6).map(_.toUpperCase)


// flattening sequence of sequence:
// e.g. obtaining the distinct element from a list of list
val adamsFriends = List("Nick K", "Bill M")
val davidsFriends = List("Becca G", "Kenny D", "Bill M")
val friendsOfFriends = List(adamsFriends, davidsFriends)
val uniqueFriends = friendsOfFriends.flatten.distinct

// flatten has a very useful effect on a sequence of Some and None elements,
// it pulls the Some element out and drops the None element
val x1 = Vector(Some(1), None, Some(3), None)
x1.flatten


// use a flatMap when we wish to call map immediately followed by a flatten.
// e.g. we were told to compute the sum of the numbers in a list, but some
// of them can't be properly converted to numbers
val bag = List("1", "2", "three", "4", "one hundred seventy five")
def toInt(s: String): Option[Int] = {
    try {
        Some(Integer.parseInt(s))
    } catch {
        case e: Exception => None
    }
}
bag.flatMap(toInt).sum


// filter walks through all of the elements in the collection
// it lets us supply a predicate (a function that returns true of false)
// and our function should return true for the elements we wish to keep;
// filter does not modify the original collection, so remember to assign
// the result to a new variable
def onlyStrings(a: Any) = a match {
    case a: String => true
    case _ => false
}
val list = "apple" :: "banana" :: 1 :: 2 :: Nil
val strings = list.filter(onlyStrings)


// extracting sequence of elements from a collection
val arr = (1 to 10).toArray

// drop method drop the number of elements from the beginning of the sequence
// there's also dropRight that drops from the end
arr.drop(2)

// dropWhile keeps dropping the element as long as the predicate we supply
// returns true
arr.dropWhile(_ < 6)

// take extracts the first N element, there's also a takeRight and takeWhile
arr.take(3)

// slice(from, until) returns a sequence beginning at the index from until the
// index until (not including the index until and assuming zero-based index)
val peeps = List("John", "Mary", "Jane", "Fred")
peeps.slice(0, 3)


// partition a sequence into two or more subsets
// the groupby method partitions the collection into a Map
val list1 = List(15, 10, 5, 8, 20, 12)
val list2 = list1.groupBy(_ > 10)
list2(true)

// partition, span, splitAt returns a Tuple2 sequence that are of the same
// type as the original collection
// partition returns two collection, one containing values for which our predicate
// returns true, the other containing elements that returns false
val (a, b) = list1.partition(_ > 10)

// span returns a Tuple2 consisting of the longest sub-sequence in the list whose
// element satisfy the predicate, and the rest of the sequence
list1.span(_ > 10)

// split at the index we've supplied
list1.splitAt(2)

// sliding(size, step) can be used to break sequence into many groups
// it can be useful when size matches step
val nums1 = (1 to 6).toArray
nums1.sliding(2, 2).toList

// unzip takes a sequence of Tuple2 values and create two resulting list;
// one containing the first element of each tuple, the other containing the second
// element from each tuple
val couples = List(("Kim", "Al"), ("Julia", "Terry"))
val (women, men) = couples.unzip
women.zip(men)


// walking through collection with reduce and fold
// reduceLeft walks through a sequence from left to right
// by passing two elements in our collection into our
// algorithm
// if the order in which the operations are performed
// on the elements is does not matter, then use reduce
val arr1 = Array(12, 6, 15, 2, 20, 9)
arr1.reduceLeft(_ + _)

// foldLeft works just like reduceLeft, but let's us
// supply the seed value
arr1.foldLeft(20)((x: Int, y: Int) => x + y)

// scanLeft walks through a sequence in a manner similar to
// foldLeft but it returns a sequence instead of a single value
val product = (x: Int, y: Int) => {
    val result = x * y
    println(s"multiplied $x by $y to yield $result")
    result
}
arr1.scanLeft(10)(product)


// to extract unique elements from a collection
// we can use .distinct or convert it to a set;
// if we want it to work for our own class, then
// we need to implement the equals and hashCode method
val x2 = Vector(1, 1, 2, 3, 3, 4)
x2.distinct
x2.toSet


// to join/merge two collections into one,
// ++= to merge a sequence into a mutable collection
val arr2 = collection.mutable.ArrayBuffer(1, 2, 3)
arr2 ++= Seq(4, 5, 6)

// ++ to merge two mutable or immutable collection
val a1 = Array(1, 2, 3)
val b1 = Array(4, 5, 6)
a1 ++ b1

// set operation
val a2 = Array(1, 2, 3, 11, 4, 12, 4, 5)
val b2 = Array(6, 7, 4, 5)
val c2 = a2.toSet diff b2.toSet
a2.intersect(b2)


// we can create collections using Range
val set = (0 to 10 by 2).toVector


// to use enumeration
// https://www.scala-lang.org/api/2.12.2/scala/Enumeration.html
object WeekDay extends Enumeration {
    // all values in the enumeration share a unique type
    type WeekDay = Value
    // each call to the Value method adds a new unique value,
    // and they are normally declared as val
    val Mon, Tue, Wed, Thu, Fri, Sat, Sun = Value
}
import WeekDay._
def isWorkingDay(d: WeekDay) = !(d == Sat || d == Sun)
WeekDay.values.filter(isWorkingDay).foreach(println)


// tuple gives us a way to store heterogeneous items in a container
val t = ("AL", "Alabama")

// we can access it through the underscore syntax though
// pattern matching it probably preferred
println(t._1)

// convert it to an iterator to loop through the tuple
for (e <- t.productIterator) println(e)


// we wish to sort a collection,
// we can use the sorted method or sortWith
List("banana", "pear", "apple", "orange").sorted

// the sortWith method lets us provide our own sorting logic,
// here we can access the element's method inside sortWith
List("banana", "pear", "apple", "orange").sortWith(_.length < _.length)

// or define the function outside
def sortByLength(s1: String, s2: String): Boolean = {
    println("comparing %s and %s".format(s1, s2))
    s1.length < s2.length
}
List("banana", "pear", "apple", "orange").sortWith(sortByLength)

// if the type of a sequence is holding doesn't have an implicit Ordering,
// then we can't sort with sorted, we'll need to resort to sortWith
class Person1(var name: String) {
    override def toString = name
}
val ty = new Person1("Tyler")
val al = new Person1("Al")
val paul = new Person1("Paul")
val dudes = List(ty, al, paul)
dudes.sortWith(_.name < _.name)

// to use the class with the sorted method, we need mix the Ordering trait
// and implement the compare method. The added benefit of mixing this trait
// is that it allows us to compare object instances directly, i.e. we can
// use <=, <, >, and >= operators
class Person2(var name: String) extends Ordered[Person2] {
    override def toString = name

    // return 0 if the same, negative if this < that, positive if this > that
    override def compare(that: Person2): Int = {
        // note that because this class only uses the String type to perform the
        // comparison, we could instead use:
        // def compare (that: Person) = this.name.compare(that.name)
        if (this.name == that.name) {
            0
        } else if (this.name > that.name) {
            1
        } else {
            -1
        }
    }
}


// we can convert collection to string, and possibly adding
// a prefix and suffix
val array = Array("apple", "banana", "cherry")
array.mkString("[", ", ", "]")
