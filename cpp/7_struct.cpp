// array of structures
// http://www.cplusplus.com/doc/tutorial/structures/
#include <iostream>
#include <string>
#include <sstream>
using namespace std;

// use the structures to define an array of them
struct movies_info {
	string title;
	int year;
} films [3];

void printmovie(movies_info movie) {
	// member of the structure can be access with the . symbol
	cout << movie.title;
	cout << " (" << movie.year << ")\n";	
}

int main() {
	int n;
	string mystr;
	
	for (n = 0; n < 3; n++) {
		cout << "Enter title: ";
		getline(cin, films[n].title);
		cout << "Enter year: ";
		getline(cin, mystr);
		stringstream(mystr) >> films[n].year;
	}

	cout << "\nYou have entered these movies:\n";
	for (n = 0; n < 3; n++) {
		printmovie(films[n]);
	}
	return 0;
}

