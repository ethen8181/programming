/*
 * Cat.cpp
 *
 *  Created on: Aug 15, 2017
 *      Author: ethen
 */

#include <iostream>
#include "Cat.h"


Cat::Cat() {
	happy = false;
}


Cat::~Cat() {
	std::cout << "Cat Destroyed" << std::endl;
}


void Cat::jump() {
	if (happy) {
		std::cout << "Jumping" << std::endl;
	}
}


void Cat::speak() {
	std::cout << "Meow" << std::endl;
}
