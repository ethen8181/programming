/*
 * udemycpp.cpp
 *
 *  Created on: Aug 14, 2017
 *      Author: ethen
 */

// the preprocessor will run and replace
// the following lines with the content in the
// actual files, thus that's why they don't have ";"
// because they are not cpp statements
#include <iostream>
#include "utils.hpp"


int main() {

	showMenu();
	int selection = getInput();
	processSelection(selection);
	return 0;
}


void showMenu() {
	std::cout << "1. Search" << std::endl;
	std::cout << "2. View Record" << std::endl;
	std::cout << "3. Quit" << std::endl;
}


int getInput() {
	std::cout << "Enter Selection: " << std::endl;
	int userInput;
	std::cin >> userInput;
	return userInput;
}


void processSelection(int selection) {
	switch (selection) {
	case 1:
		std::cout << "Searching" << std::endl;
		break;
	case 2:
		std::cout << "Viewing" << std::endl;
		break;
	case 3:
		std::cout << "Quitting" << std::endl;
		break;
	default:
		std::cout << "Please select an item from the menu" << std::endl;
	}
}
