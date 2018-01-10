//============================================================================
// Name        : Inheritance.cpp
// Author      : Ethen
// Version     :
// Copyright   : Your copyright notice
// Description : Hello World in C++, Ansi-style
//============================================================================

#include <iostream>
using namespace std;

class Animal {
public:
	void speak() {
		cout << "Grrrr" << endl;
	}
};

// Cat is going to be a sub-class of Animal and Animal
// is a superclass of Cat
// so it will automatically inherit the speak method;
class Cat: public Animal {

// we will also define methods that are specific to Cat and
// not to a generic Animal
public:
	void jump() {
		cout << "Cat Jumping" << endl;
	}
};


class Machine {
private:
	int id;

public:
	Machine(): id(0) {
		cout << "Machine called" << endl;
	}

	Machine(int id): id(id) {
		cout << "Machine parameterized constructor called" << endl;
	}
};

class Vehicle: public Machine {
public:
	// specify that we wish to call the Machine constructor
	// that instantiate the id that's private to the Machine
	// class, i.e. we can't modify id in the subclass
	Vehicle(int id): Machine(id) {
		cout << "Vehicle called" << endl;
	}
};


int main() {
	Animal a;
	a.speak();

	Cat cat;
	cat.speak();
	cat.jump();

	// our Vehicle class inherits Machine;
	// and we instantiate an object of that class,
	// it will call the constructor of the parent class
	// before calling the constructor of the class;
	// and during the initialization we can also specify
	// which constructor will be called in the parent class
	Vehicle vehicle(999);

	return 0;
}
