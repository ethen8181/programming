
// different ways to populate a List
// this class is implemented as a linked list
// thus it is suitable for last in first out
// stack-like access patterns. List has O(1)
// prepend and head/tail access
List.fill(3)("foo")
List.range(0, 5)
List.tabulate(5)(_ + 1)

// List are immutable, but we can still create
// a new List from an original one, typically
// we would preprend items to the original List,
// the :: method is right associative, meaning
// the list is constructed from right to left
val x = List(2)
val y = 1 :: x

// or rather than continually reassigning it to a new
// variable, we can declare our variable as var and
// reassign the result to it
var x1 = List(2)
x1 = 1 :: x1

// though the :: method is pretty common, there are other
// methods that lets us prepend
0 +: x1

// or append
x1 :+ 3


// merging two Lists using ++, ::: or concat
val a1 = List(1, 2, 3)
val b1 = List(4, 5, 6)
a1 ++ b1
List.concat(a1, b1)
a1 ::: b1

// we can use a mutable list ListBuffer
import scala.collection.mutable.ListBuffer
var fruits = new ListBuffer[String]()

// add one element at a time
fruits += "Apple"
fruits += "Banana"

// add multiple elements
fruits += ("Strawberry", "Kiwi")

// add elements from another sequence
fruits ++= Seq("Pineapple")

// convert it to an immutable List when we need to
val fruitsList = fruits.toList

// if we are going to be modifying the list frequently,
// it may be better to use List
val list1 = ListBuffer(1, 2, 3, 4, 5, 6, 7, 8, 9)

// delete one element
list1 -= 5
println(list1)

// delete by position
list1.remove(0)
println(list1)

// delete from a starting position and provide the number
// of elements to delete
list1.remove(1, 3)
println(list1)


// scala Array corresponds to Java array, i.e. Array[Int] = int[]
// it's mutable in a sense that we can change its element, but
// its size can't change, to create a mutable, indexed sequence
// use the ArrayBuffer class
val arr1 = Array(1, 2, 3)
arr1(0) = 0
arr1.foreach(println)

// create an array with an initial size
// and populate it later
val arr2 = new Array[String](3)
arr2(0) = "Apple"
arr2(1) = "Banana"
arr2(2) = "Orange"
arr2.foreach(println)

// create multidimensional array
// the .ofDim approach is unique to Array
val rows = 2
val cols = 3
val arr3 = Array.ofDim[String](rows, cols)
arr3(0)(0) = "a"
arr3(0)(1) = "b"
arr3(0)(2) = "c"
arr3(1)(0) = "d"
arr3(1)(1) = "e"
arr3(1)(2) = "f"
for {
    i <- 0 until rows
    j <- 0 until cols
} println(s"($i)($j) = ${arr3(i)(j)}")

// on the other hand, array of array is not
// unique to Array, we can have vector of vector
// or list of list
Array(Array("a", "b", "c"), Array("d", "e", "f"))


// Maps
// the following syntax creates a tuple
"AL" -> "Alabama"

// thus we can use either methods to create the Map
Map("AL" -> "Alabama", "AK" -> "Alaska")
Map(("AL", "Alabama"), ("AK", "Alaska"))

// to create a mutable Map
import scala.collection.mutable.{Map => MMap}
var states = MMap[String, String]()

// add elements using += operator
states += ("AL" -> "Alabama")

// add multiple elements from another collection
states ++= List("CA" -> "California", "CO" -> "Colorado")

// provide a new key-value pair
// if states was an immutable Map, then
// this would fail
states("AK") = "Alaska"

// we delete element by key
states -= "AL"

// the put method: if the element put into the map
// collection replaces another element, the value
// would be returned
states.put("CO", "Colorados")

// and the remove method returns an Option that
// contains the value that was removed
states.remove("AK")

// retain keep only the elements in the map
// that matches the predicate we supply
states.retain((k, _) => k == "CO")

// different ways to access map values
val state1 = Map("AL" -> "Alabama", "AK" -> "Alaska", "AZ" -> "Arizona")

// check whether a Map contains a given key
state1.contains("Foo")

// we can access using our Map's key,
// note that this will return an NoSuchElementException
// error if the map doesn't contain the requested key
state1("AK")

// we can use the get method, which returns an Option
state1.get("AZ")

// or use the getOrElse method and specify the default value
state1.getOrElse("AZ", "Not Found")

// or create the map with an additional withDefaultValue method
val state2 = Map("AL" -> "Alabama").withDefaultValue("Not found")
state2("foo")

// different ways of iterating over a Map
// the transform method gives us a way to create new
// map from an existing map using a key and value
val map1 = Map(1 -> 10, 2 -> 20, 3 -> 30)
map1.transform((k, v) => k + v)

// if we wish to operate only on the values, then use mapValues
var map2 = Map(1 -> "a", 2 -> "b")
map2.mapValues(_.toUpperCase)

// for loop
for ((k, v) <- map2) println(s"key: $k, value: $v")

// foreach match expression
map2.foreach {
    case(k, v) => println(s"key: $k, value: $v")
}

// if we just want the key or value
map2.keys.foreach(println)
map2.values.foreach(println)

// obtaining the key/value from a Map
val states1 = Map("AK" -> "Alaska", "AL" -> "Alabama", "AR" -> "Arkansas")

// returns a Set
states1.keySet

// returns a lightweight iterator
// http://docs.scala-lang.org/overviews/collections/iterators.html
states1.keysIterator

// we can use a foreach method to step through all the elements from
// the iterator
val it1 = Iterator("a", "number", "of", "words")
it1.foreach(println)

// after looping through the iterator, the iterator will be exhausted,
// i.e. it becomes an empty iterator. Hence, if we were to loop through
// the elements twice, we would need to duplicate the iterator
val (words, ns) = Iterator("a", "number", "of", "words").duplicate
val shorts = words.filter(_.length < 3).toList
val count = ns.map(_.length).sum

// to reverse key and value pair;
// be aware a Map's value don't have to be unique,
// so we might lose some content when we perform this reverse mapping
val products = Map(
    "Breadsticks" -> "$5",
    "Pizza" -> "$10",
    "Wings" -> "$5")
val reversedMap = for ((k, v) <- products) yield (v, k)

// obtaining the largest value in a map
val grades = Map("Al" -> 80, "Kim" -> 95, "Teri" -> 85, "Julia" -> 90)

// returns the key/value pair that has the maximum key
grades.max

// just the maximum key
grades.keysIterator.max
grades.keysIterator.reduceLeft((x, y) => if (x > y) x else y)

// sort the elements in the Map by its key;
// to achieve this we can convert the Map to a sequence and
// use its sorting method
grades.toSeq.sortBy(_._1)


// adding elements to a Set
// the unique characteristic of add/remove is that it returns
// a boolean value of whether or not the element was
// successfully added/removed
val set1 = scala.collection.mutable.Set[Int](1, 2, 3)
set1.add(1)
set1.remove(1)
set1


// queue (FIFO), we can add elements using the += operator
// or the enqueue method
import scala.collection.mutable.Queue
var q = Queue[String]()
q += "apple"
q.enqueue("pineapple")
q

// we typically remove one element at a time from the head of the queue
val next = q.dequeue
q


// Stack is a LIFO data structure, in most programming languages, we add
// elements to a stack using a push method and take elements off using
// the pop method. Scala is no different;
// note that there's also the ArrayStack and according to the Scala documentation
// it provides fast indexing and is generally slightly more efficient than the
// normal mutable Stack class
import scala.collection.mutable.Stack

val fruits1 = Stack[String]()
fruits1.push("coconut", "orange", "pineapple")
val fruit1 = fruits1.pop