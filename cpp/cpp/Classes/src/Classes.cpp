//============================================================================
// Name        : Classes.cpp
// Author      : Ethen
// Version     :
// Copyright   : Your copyright notice
// Description : Hello World in C++, Ansi-style
//============================================================================

#include <iostream>
#include "Cat.h"
using namespace std;

int main() {
	// instantiate a cat object
	Cat cat;
	cat.speak();
	cat.jump();

	// char array
	// when looping through the array, we noticed that
	// the sizeof(char array) is returning 6 as oppose to 5,
	// this is because the last element is the string/null terminator,
	// this is used to let the program know where the string ends
	char text[] = "hello";
	for (unsigned int i = 0; i < sizeof(text); i++) {
		std::cout << i << ": " << (int)text[i] << std::endl;
	}

	// to get the length of the string, we subtract by 1 to
	// exclude the null terminator
	int len = sizeof(text) - 1;

	// reverse the string
	char *start = text;
	char *end = text + len - 1;
	while (start < end) {
		char temp = *start;
		*start = *end;
		*end = temp;
		start++;
		end--;
	}
	std::cout << text << std::endl;

	return 0;
}
