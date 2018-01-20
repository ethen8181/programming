package foo

// scala /Users/ethen/IdeaProjects/MyProject/target/scala-2.12/myproject_2.12-0.1.jar
// to execute the main method

case class Person(var name: String)

object Main extends App {
    val p = Person("Alvin Alexander")
    println("Hello from " + p.name)
}


// ? 18.6 creating a project with subprojects