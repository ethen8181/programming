// function template
// http://www.cplusplus.com/doc/tutorial/functions2/
// http://stackoverflow.com/questions/5687540/non-type-template-parameters
#include <iostream>
using namespace std;

/* 
the method sum could be overloaded with a lot of types,
i.e. we could sum up two integers or two doubles. And in
this case it makes sense for them to have the same body;
in C++, we have the ability to define functions with generic
types, known as function templates
*/
template<class T> // the class keyword can also be replaced as typename
T sum(T a, T b) {
	// notice that the generic type T is also used
	// to declare the local variable
	T result; 
	result = a + b;
	return result;
}

int main () {
	int i = 5, j = 6, k;
	double f = 2.0, g = 0.5, h;
	k = sum<int>(i, j);
	h = sum<double>(f, g);
	cout << k << '\n';
	cout << h << '\n';
	return 0;
}



