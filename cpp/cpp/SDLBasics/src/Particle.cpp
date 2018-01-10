/*
 * Particle.cpp
 *
 *  Created on: Aug 26, 2017
 *      Author: ethen
 */

#include <math.h>
#include <stdlib.h>
#include "Particle.h"

namespace basics {

Particle::Particle() {
	init();
}

Particle::~Particle() {
	// TODO Auto-generated destructor stub
}

void Particle::init() {
	x = 0;
	y = 0;

	// speed: random number between 0 to 1, so the
	// particles in different speed, the number up front
	// is simply an adjustable multiplier to control the
	// smoothness of the transition
	speed = (0.04 * rand()) / RAND_MAX;

	// squaring speed so the speed isn't uniformly distributed
	speed *= speed;

	// use radian to represent the direction
	direction = (2 * M_PI * rand()) / RAND_MAX;
}

void Particle::update(int interval) {
	direction += interval * 0.0003;
	double xspeed = speed * cos(direction);
	double yspeed = speed * sin(direction);
	x += xspeed * interval;
	y += yspeed * interval;

	if (x < -1 || x > 1 || y < -1 || y > 1) {
		init();
	}

	if(rand() < RAND_MAX / 100) {
		init();
	}
}

} /* namespace basics */
