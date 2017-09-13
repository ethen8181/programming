//============================================================================
// Name        : SDLBasics.cpp
// Author      : Ethen
// Version     :
// Copyright   : Your copyright notice
// Description : Hello World in C++, Ansi-style
//============================================================================

#include <iostream>
#include <math.h>
#include <SDL.h>
#include "Screen.h"
#include "Swarm.h"
using namespace std;
using namespace basics;

int main() {
	srand(time(NULL));
	Screen screen;
	if (!screen.init()) {
		cout << "failed" << endl;
	}

	// this is the game loop, or so called event loop;
	// where it will continuously run throughout the
	// lifetime of the game or program
	Swarm swarm;
	while (true) {

		// create the transition of colors using the sin (cos also works)
		// sin takes a value and squashes it between -1 and 1, and when we
		// add 1 it will range between 0 and 2, then we can multiply by 128
		// so the range will be 0 ~ 256, which is the range that the RGB value
		// can take; the multiplier with the current elapse time is to make
		// the transition a bit smoother (smaller value makes changes less abrupt).
		// and we can supply different multiplier so the transition rate will be
		// different for each color
		int elapsed = SDL_GetTicks();
		Uint8 red = (1 + sin(elapsed * 0.0001)) * 128;
		Uint8 green = (1 + sin(elapsed * 0.0002)) * 128;
		Uint8 blue = (1 + sin(elapsed * 0.0003)) * 128;

		// update position of all particles
		swarm.update(elapsed);

		Particle* pParticles = swarm.getParticles();
		for (int i = 0; i < Swarm::NPARTICLES; i++) {
			Particle particle = pParticles[i];
			int x = (particle.x + 1) * Screen::SCREEN_WIDTH / 2;
			int y = particle.y * Screen::SCREEN_WIDTH / 2 + Screen::SCREEN_HEIGHT / 2;
			screen.setPixel(x, y, red, green, blue);
		}
		screen.boxBlur();

		// Draw the screen
		screen.update();
		if(!screen.processEvents()) {
			break;
		}
	}

	return 0;
}
