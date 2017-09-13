/*
 * Cat.h
 *
 *  Created on: Aug 15, 2017
 *      Author: ethen
 */

#ifndef CAT_H_
#define CAT_H_

class Cat {
public:
	// constructor/destructor has to be the same name as the class
	// and it doesn't have to have a type in front since
	// they don't return anything
	Cat();
	~Cat();
	void speak();
	void jump();

private:
	bool happy;
};

#endif /* CAT_H_ */
