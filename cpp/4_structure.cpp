// passing parameters by reference
#include <iostream>
using namespace std;

/*
C++ allows us the pass arguments by reference as
oppose to value. This means that, when calling a function, 
what is passed to the function are copied into the variables
represented by the function parameters. Thus any modification 
of these variables within the function has no effect on the 
values of the variables x and y outside it;
In certain cases, though, it may be useful to access an external 
variable from within a function. To do that, 
arguments can be passed by reference using & sign
*/
void duplicate(int& a, int& b, int& c) {
	a *= 2;
	b *= 2;
	c *= 2;
}

int main() {
	int x = 1, y = 3, z = 7;
	duplicate(x, y, z);
	cout << "x=" << x << ", y=" << y << ", z=" << z;
	return 0;
}



