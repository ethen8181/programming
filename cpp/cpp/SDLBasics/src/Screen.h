/*
 * Screen.h
 *
 *  Created on: Aug 26, 2017
 *      Author: ethen
 */

#ifndef SCREEN_H_
#define SCREEN_H_

#include <SDL.h>

namespace basics {

class Screen {
public:
	// we only need one value for these constant value,
	// thus set it to static to be shared across all class
	const static int SCREEN_WIDTH = 800;
	const static int SCREEN_HEIGHT = 600;

	Screen();
	bool init();
	bool processEvents();
	void setPixel(int x, int y, Uint8 red, Uint8 green, Uint8 blue);
	void update();
	void boxBlur();
	void close();

private:
	SDL_Window* window;
	SDL_Renderer* renderer;
	SDL_Texture* texture;
	Uint32* bufferColor;
	Uint32* bufferBlur;
};

} /* namespace basics */

#endif /* SCREEN_H_ */
