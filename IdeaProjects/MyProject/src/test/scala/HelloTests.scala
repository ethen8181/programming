package foo

import org.scalatest.FunSuite

// running test with ScalaTest
class HelloTests extends FunSuite {
    test("the name is set correctly in the constructor") {
        val p = Person("Barney Rubble")
        assert(p.name == "Barney Rubble")
    }

    test("a Person's name can be changed") {
        val p = Person("Chad Johnson")
        p.name = "Ochocinco"
        assert(p.name == "Ochocinco")
    }
}
