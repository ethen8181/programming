package com.headfirstjava;

import java.io.Serializable;


class Employee implements Serializable {
    public String name;
    public String address;
    public transient int SSN;
    public int number;

    public void mailCheck() {
        System.out.println("Mailing a check to " + name + " " + address);
    }
}

/*
Compiling java code

first we compile our java code
the -d flag tells which directory the compiled code lands in:
javac -d ../classes com/headfirst/*.java

after that, we can run:
java com.headfirstjava.MyApp

to execute the compiled java code.
*/

/*
Putting our java code in a JAR (Java ARchive):
we only need to provide the com directory, and the entire
package and all its classes will go into the JAR
jar -cvmf manifest.txt app1.jar com

Running the JAR:
Java (the JVM) is capable of loading a class from a JAR
and calling the main method of that class. It does this
by looking inside this JAR for a manifest that has an Main-Class
entry.
java -jar app1.jar
*/
public class MyApp {

    public static void main(String []args) {
        Employee employee = new Employee();
        employee.name = "Ethen";
        employee.address = "Liu";
        employee.mailCheck();
    }
}
