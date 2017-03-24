// http://www.cplusplus.com/doc/tutorial/basic_io/
#include <string>
#include <sstream>
#include <iostream>
using namespace std;

int main() {
	int price = 0;
	string mystr;
	cout << "The Price is: ";

	// getline allows us to obtain multiple elements
	// as oppose to just one, convert the string into
	// an integer
	getline(cin, mystr);

	// http://stackoverflow.com/questions/200090/how-do-you-convert-a-c-string-to-an-int
	stringstream(mystr) >> price;
	cout << "Two costed: " << 2 * price << ".\n";

	return 0;
}



