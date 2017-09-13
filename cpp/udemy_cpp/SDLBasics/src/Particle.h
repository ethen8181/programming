/*
 * Particle.h
 *
 *  Created on: Aug 26, 2017
 *      Author: ethen
 */

#ifndef PARTICLE_H_
#define PARTICLE_H_

namespace basics {

class Particle {
public:
	Particle();
	virtual ~Particle();
	void update(int interval);

	// allows gradually transition in position by
	// making the x, y coordinate double
	double x;
	double y;

private:
	double speed;
	double direction;
	void init();
};

} /* namespace basics */

#endif /* PARTICLE_H_ */
