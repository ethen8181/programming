//============================================================================
// Name        : FunctionPointers2.cpp
// Author      : Ethen
// Version     :
// Copyright   : Your copyright notice
// Description : Hello World in C++, Ansi-style
//============================================================================

#include <iostream>
using namespace std;


class Parent {
private:
	int one;

public:
	// subclass runs the constructor of the parent class in order
	// to be instantiated, so when we define a subclass, we must
	// either have a default constructor in the parent class or
	// else we have to specify what constructor we wish to run;
	// so when we define our own copy constructor, we lose the implicit
	// default constructor
	Parent(): one(0) {

	}

	Parent(const Parent &other) {
		one = other.one;
		cout << "copy parent" << endl;
	}

	virtual void print() {
		cout << "parent" << endl;
	}

	virtual ~Parent() {

	}
};

// when an object that was created on the stack is destroyed,
// the child class destructor is called first, then the parent class;
// thus we should make sure we have a virtual destructor so that if our
// child allocates memory and frees it in its destructor it will get called
// by the compiler
class Child: public Parent {

public:
	// it will run the default constructor of the parent class
	void print() {
		cout << "child" << endl;
	}
};


// abstract class
class Animal {
public:
	// setting it = 0 implies that it's a pure virtual function
	virtual void speak() = 0;
	virtual ~Animal() {};
};

class Dog: public Animal {
public:
	// must provide actual implementation for the pure virtual function
	virtual void speak() {
		cout << "Woof" << endl;
	}

	virtual ~Dog() {};
};


// functor is a class or a struct that overloads
// the bracket operator
struct Test {
	virtual bool operator()(string &text) = 0;
	virtual ~Test() {};
};

struct MatchTest: public Test {
	// overload the () operator
 	bool operator()(string &text) {
 		return text == "lion";
 	}
};

void check(string text, Test &test) {
	// check might be able to perform different types of test
	if (test(text)) {
		cout << "Text match" << endl;
	} else {
		cout << "No match" << endl;
	}
}

int main() {
	Child c1;
	Parent &p1 = c1;
	p1.print();

	Parent p2 = Child();
	p2.print();


	// functors as oppose to function pointers
	MatchTest match;
	string value = "lion";
	cout << match(value) << endl;
	check(value, match);
	return 0;
}
