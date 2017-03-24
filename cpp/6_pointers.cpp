// pointers are said to point to the variable whose
// address they store
// http://www.cplusplus.com/doc/tutorial/pointers/

// pointers as arguments:
#include <iostream>
using namespace std;

void increment_all(int* start, int* stop) {
	// use * after the type to declare that it's a pointer
	// do not confuse this with the dereference operator
	while (start != stop) {
		// * is the dereference operator, 
		// and can be read as "value pointed to by"
		// increment value pointed
		(*start)++;  
		cout << *start << endl;

		// increment pointer
		start++;
	}
}

int main() {
	int numbers[] = {10, 20, 30};

	// array can be converted to pointer of the proper type
	increment_all(numbers, numbers + 3);
	return 0;
}
