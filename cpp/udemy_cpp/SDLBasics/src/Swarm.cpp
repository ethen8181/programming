/*
 * Swarm.cpp
 *
 *  Created on: Aug 26, 2017
 *      Author: ethen
 */

#include "Swarm.h"

namespace basics {

Swarm::Swarm(): previousTime(0) {
	pParticles = new Particle[NPARTICLES];
}

Swarm::~Swarm() {
	delete [] pParticles;
}

void Swarm::update(int elapsed) {
	// interval serves as a multiplicative constant
	// to ensure that the speed is moving approximately
	// the same regardless of the speed of the operating system,
	// i.e. how fast the event loop is executed
	int interval = elapsed - previousTime;
	for (int i = 0; i < NPARTICLES; i++) {
		pParticles[i].update(interval);
	}
	previousTime = elapsed;
}

} /* namespace basics */
