/*
 * Swarm.h
 *
 *  Created on: Aug 26, 2017
 *      Author: ethen
 */

#ifndef SWARM_H_
#define SWARM_H_

#include "Particle.h"

namespace basics {

class Swarm {
public:
	Swarm();
	// virtual ensures when we subclass the class, it will
	// call the appropriate method (so destructor should always
	// be virtual, since we want to make sure it's using the proper
	// method is clean up the memory)
	virtual ~Swarm();
	const static int NPARTICLES = 5000;
	Particle* getParticles() {return pParticles;};
	void update(int elapsed);

private:
	int previousTime;
	Particle* pParticles;
};

} /* namespace basics */

#endif /* SWARM_H_ */
