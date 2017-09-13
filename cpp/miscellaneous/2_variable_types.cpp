// http://www.cplusplus.com/doc/tutorial/variables/

#include <string>
#include <iostream>

// will be explained more in the future, but this allows
// use function from the std library without calling std:: in front
using namespace std;

int main() {
	// declaring variables:
	int a, b;
	int result;

	// process:
	a = 5;
	b = 2;
	a = a + 1;
	result = a - b;

	// print out the result and indicate that it's the end of the line:
	cout << result << endl;

	string mystring = "This is a string";
	cout << mystring << endl;

	// terminate the program:
	return 0;
}