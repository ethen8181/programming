// namespaces
// group global variables that would have caused
// naming collision

#include <iostream>
using namespace std;

namespace foo {
	int value() { 
		return 5;
	}
}

namespace bar {
	// inside the namespace, variables
	// can be accessed directly, but outside
	// we have to use the scope operator ::
	const double pi = 3.1416;
	double value() { 
		return 2 * pi;
	}
}

int main () { 
	cout << foo::value() << '\n';
	cout << bar::value() << '\n';
	cout << bar::pi << '\n';
	// The keyword using introduces a name into the 
	// current declarative region (such as a block), 
	// thus avoiding the need to qualify the name
	return 0;
}

