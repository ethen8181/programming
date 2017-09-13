//============================================================================
// Name        : Exception.cpp
// Author      : Ethen
// Version     :
// Copyright   : Your copyright notice
// Description : Hello World in C++, Ansi-style
//============================================================================

#include <iostream>
#include <exception>
using namespace std;

void mightGoWrong() {
	bool error1 = false;

	// as soon as we do a throw exception, we go straight out of
	// the function
	if (error1) {
		throw "Something went wrong";
	}

	bool error2 = true;
	if (error2) {
		throw string("Something went wrong");
	}
}


class CanGoWrong {
public:
	CanGoWrong() {
		// can't allocate memory since the integer we
		// requested is too large, the exception should
		// be std::bad_alloc
		char* pMemory = new char[99];
		delete[] pMemory;
	}
};

class MyException: public exception {
	// https://www.tutorialspoint.com/cplusplus/cpp_exceptions_handling.htm
	// to implement our own exception class, we should override the what method
	// of the exception parent class
	const char* what() const throw() {
		// const throw means that the method can't throw an exception
		return "C++ Exception";
	}
};


int main() {

	try {
		mightGoWrong();
	} catch (int e) {
		cout << "Error code: " << e << endl;
	} catch (char const* e) {
		cout << "Error message: " << e << endl;
	} catch (string &e) {
		// standard way of referencing the exception
		// when the exception is an object
		cout << "String error message: " << e << endl;
	}


	try {
		CanGoWrong wrong;
	} catch (bad_alloc &e) {
		// remember to always put the exception subclass (in this
		// case bad_alloc is a subclass of exception) before the
		// base class catch block. This ensures we know what we're
		// actually catching
		cout << e.what() << endl;
	} catch (exception &e) {
		cout << "exception base class" << e.what() << endl;
	}

	return 0;
}
