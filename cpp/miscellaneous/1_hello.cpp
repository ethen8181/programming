// http://www.cplusplus.com/doc/tutorial/program_structure/
// my first program

/* 
# are directives which are read and interpreted before
the compilation of the program; the header allows us
to perform standard input and ouput operations 
*/
#include <iostream>

// the execution of the c++ program begins in the main function
int main() {
	// all the elements in the c++ standard library are declared
	// in a namespace, in order to refer to the std namespace, 
	// we include the std:: prefix to qualify each and every use
	// of the library's elements
	std::cout << "Hello World!";
	std::cout << "I'm a C++ program";
}