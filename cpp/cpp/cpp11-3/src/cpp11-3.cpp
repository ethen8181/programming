//============================================================================
// Name        : cpp11-3.cpp
// Author      : Ethen
// Version     :
// Copyright   : Your copyright notice
// Description : Hello World in C++, Ansi-style
//============================================================================

#include <iostream>
#include <memory>  // unique_ptr
#include <functional>
using namespace std;

class Parent {
public:
	virtual ~Parent() {

	}
};

class Brother: public Parent {

};


int add(int a, int b) {
	return a + b;
}

class Test {

};

class Temp {
private:
	unique_ptr<int[]> ptr;

public:
	Temp(): ptr(new int[2]) {

	}
};

int main() {
	// c-style casting float to integer
	// both type of casting works:
	float value = 3.23;
	cout << int(value) << endl;
	cout << (int)value << endl;

	// cpp style static_cast,
	// note that it does not perform checking for
	// you, it's up to us to make sure our casting
	// is sensible
	cout << static_cast<int>(value) << endl;

	// dynamic cast: runtime checking (static cast
	// does not have it)
	// we can perform downcasting,
	// pointing a parent class at the child pointer
	// and if this happens, the resulting pointer will
	// be a null pointer (because the child might have
	// methods that the parent does not have, thus when
	// we call it just like any child, the code will crash)
	Parent parent;
	Brother* brother = dynamic_cast<Brother*>(&parent);

	// check at runtime
	if (brother == nullptr) {
		cout << "Invalid";
	} else {
		cout << brother;
	}
	cout << endl;

	// bind, alias to functions
	auto calculate = bind(add, 1, 2);
	cout << calculate() << endl;


	// unique_ptr, automatically deallocates the allocated memory,
	// note that allocated memory goes inside the constructor
	unique_ptr<int> ptest(new int);
	*ptest = 7;
	cout << *ptest << endl;


	Temp temp;
	return 0;
}
