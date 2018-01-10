/*
 * Screen.cpp
 *
 *  Created on: Aug 26, 2017
 *      Author: ethen
 */

#include "Screen.h"

namespace basics {

Screen::Screen() {
	// we initialize them at the init method instead,
	// since constructor can't return value, and we wish
	// to have a bool return type to indicate whether
	// they were successfully initialized
	window = NULL;
	renderer = NULL;
	texture = NULL;
	bufferColor = NULL;
	bufferBlur = NULL;
}


bool Screen::init() {
	if (SDL_Init(SDL_INIT_VIDEO) < 0) {
		return false;
	}

	window = SDL_CreateWindow(
		"Particle Swarm Explosion",
		SDL_WINDOWPOS_UNDEFINED, SDL_WINDOWPOS_UNDEFINED,
		SCREEN_WIDTH, SCREEN_HEIGHT, SDL_WINDOW_SHOWN);

	if (window == NULL) {
		SDL_Quit();
		return false;
	}

	// last flags ensure we're synchronized with the refresh rate of the window
	renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_PRESENTVSYNC);
	texture = SDL_CreateTexture(
		renderer, SDL_PIXELFORMAT_RGBA8888, SDL_TEXTUREACCESS_STATIC, SCREEN_WIDTH, SCREEN_HEIGHT);


	// allocate enough memory to represent all the pixels on the screen
	bufferColor = new Uint32[SCREEN_WIDTH * SCREEN_HEIGHT];
	bufferBlur = new Uint32[SCREEN_WIDTH * SCREEN_HEIGHT];

	// set a block of memory with some particular value
	memset(bufferColor, 0, SCREEN_WIDTH * SCREEN_HEIGHT * sizeof(Uint32));
	memset(bufferBlur, 0, SCREEN_WIDTH * SCREEN_HEIGHT * sizeof(Uint32));
	return true;
}


void Screen::setPixel(int x, int y, Uint8 red, Uint8 green, Uint8 blue) {
	// ensure we don't draw off the screen
	if(x < 0 || x >= SCREEN_WIDTH || y < 0 || y >= SCREEN_HEIGHT) {
		return;
	}

	// color format: RBGA, ignore the A (alpha)
	// 255 is the max value we can put in a byte, instead of writing 255,
	// we'll write it in hexidecimal, and 0x is a prefix to say its a
	// hexidecimal number (here we need two digits to specify 1 byte)
	Uint32 color = 0;
	color += red;
	color <<= 8;
	color += green;
	color <<= 8;
	color += blue;
	color <<= 8;
	color += 0xFF;
	bufferColor[(y * SCREEN_WIDTH) + x] = color;
}


void Screen::boxBlur() {
	Uint32* temp = bufferColor;
	bufferColor = bufferBlur;
	bufferBlur = temp;

	// for every position compute the average color of the surrounding pixel
	for (int x = 0; x < SCREEN_WIDTH; x++) {
		for (int y = 0; y < SCREEN_HEIGHT; y++) {

			int redTotal = 0;
			int greenTotal = 0;
			int blueTotal = 0;

			// assuming we're averaging the color of a the 3 times 3 box
			for (int row = -1; row < 1; row++) {
				for (int col = -1; col < 1; col++) {
					int xBox = x + row;
					int yBox = y + col;
					if (xBox >= 0 && xBox < SCREEN_WIDTH && yBox >= 0 && yBox < SCREEN_HEIGHT) {
						Uint32 color = bufferBlur[yBox * SCREEN_WIDTH + xBox];
						Uint8 red = color >> 24;
						Uint8 green = color >> 16;
						Uint8 blue = color >> 8;
						redTotal += red;
						greenTotal += green;
						blueTotal += blue;
					}
				}
			}
			int redAvg = redTotal / 9;
			int greenAvg = greenTotal / 9;
			int blueAvg = blueTotal / 9;
			setPixel(x, y, redAvg, greenAvg, blueAvg);
		}
	}
}

void Screen::update() {
	// update the texture with information from the buffer;
	// then tell the renderer to render/draw the texture
	SDL_UpdateTexture(texture, NULL, bufferColor, SCREEN_WIDTH * sizeof(Uint32));

	// clear the entire screen
	SDL_RenderClear(renderer);

	// copy the texture to the renderer
	SDL_RenderCopy(renderer, texture, NULL, NULL);

	// Up until now everything was drawn behind the scenes.
    // This will show the new contents of the window
	SDL_RenderPresent(renderer);
}


bool Screen::processEvents() {
	// check the ensure there's an event
	// that's waiting to be processed
	SDL_Event event;
	while (SDL_PollEvent(&event)) {
		if (event.type == SDL_QUIT) {
			return false;
		}
	}
	return true;
}


void Screen::close() {
	delete [] bufferColor;
	delete [] bufferBlur;
	SDL_DestroyRenderer(renderer);
	SDL_DestroyTexture(texture);
	SDL_DestroyWindow(window);
	SDL_Quit();
}

} /* namespace basics */
