//============================================================================
// Name        : NewOperator.cpp
// Author      : Ethen
// Version     :
// Copyright   : Your copyright notice
// Description : Hello World in C++, Ansi-style
//============================================================================

#include <iostream>
using namespace std;

class Animal {
private:
	string name;

public:
	Animal() {
		cout << "Animal created" << endl;
	}

	Animal(const Animal &other) : name(other.name) {
		cout << "Animal created by copying" << endl;
	}

	~Animal() {
		// the destructor runs right before
		// the memory of the object is deallocated
		cout << "Destructor called" << endl;
	}

	void setName(string name) {
		this->name = name;
	}

	void speak() const {
		cout << "My name is " << name << endl;
	}
};

Animal *createAnimal() {
	// returning objects from functions
	// by using pointers, we can prevent
	// generating a copy of the object,
	// now we're potentially just copying
	// the size of the pointer instead of
	// the size of the object
	Animal *pAnimal = new Animal();
	pAnimal->setName("Bertie");
	return pAnimal;
}

int main() {
	// the standard way of instantiating a class
	Animal cat;
	cat.setName("Freddy");
	cat.speak();

	// the new operator allocates memory explicit,
	// and this will be the memory that we manage ourselves
	// and when we do this, we must always remember to
	// remove the object ourselves to free up the memory
	Animal *pcat1 = new Animal();

	// instead of writing the unwieldy (*pcat1).setName("Bob")
	// to deference the object and then calling the method, there's
	// an -> operator that does the exact same thing
	pcat1->setName("Bob");
	pcat1->speak();

	// 1. delete the allocated memory, just remember that for
	// every new operator there has to be a corresponding delete operator;
	// or else it will cause memory leaks;
	// 2. remember to not delete pointers that have been instantiated
	// using the new operator
	delete pcat1;

	// pointer has the size of long
	cout << sizeof(long) << endl;
	cout << sizeof(pcat1) << endl;


	// again we need to call delete since
	// the pcat2 pointer is instantiated using new
	Animal *pcat2 = createAnimal();
	pcat2->speak();
	delete pcat2;


	// allocating a block of memory using the bracket syntax, []
	// and specifying the number inside the bracket; then
	// we can also use the [] syntax to delete the allocated block
	// of memory, although this time we won't need to specify the
	// number inside
	Animal *pAnimal = new Animal[2];

	// here we are defining a Pointer to an array of objects,
	// thus when we access the nth element using the bracket syntax,
	// we are referring to the nth object of the array that it's pointing to
	pAnimal[1].setName("Tess");
	pAnimal[1].speak();
	delete [] pAnimal;
	// or we could provide a utility function to clean the memory

	// since char is basically a representation of the ASCII
	// table, we can increment it using the ++ operator
	char c = 'a';
	c++;
	cout << c << endl;

	// we can actually convert a char to a string, using
	// the following syntax, where the first element represents
	// how many char there is
	string str(1, c);
	cout << str << endl;

	cout << "Program ended" << endl;
	return 0;
}
