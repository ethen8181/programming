
// we can import multiple classes the Scala way
import java.io.{File, IOException, FileNotFoundException}

// or import everything using the _ syntax
// this can be useful technique when importing enum,
// as enum tend to be more readable as is without
// specifying the name of the class or enum before the constant
import java.io._

// we can rename things during import to prevent name collision
import java.util.{ArrayList => JArrayList}

// we now we can refer to the renamed import
val list = new JArrayList[String]