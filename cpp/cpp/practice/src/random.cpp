/*
 * random.cpp
 *
 *  Created on: Apr 12, 2017
 *      Author: ethen
 */

#include <vector>
#include <iostream>
#include <algorithm> // std::random_shuffle, std::swap
#include <random>
#include "rand.hpp"

#include <string>
#include <unordered_set>

int main() {

	std::vector<float> a(100);
	for(int i = 0; i < 100; ++i) {
		a[i] = i * 1.5;
	}

	int seed = 314;
	int n_random = 10;
	std::vector<float> b = random_choice(a, n_random, seed);

	std::cout << "output" << "\n";
	b.resize(n_random);
	std::cout << b.size() << "\n";
	for(int i = 0; i < n_random; ++i) {
		std::cout << b[i] << " ";
	}

	/*
	std::cout << '\n';
	//int seed = 3412;
	int left1 = 10;
	std::default_random_engine random_engine(seed);
	std::uniform_int_distribution<int> uniform_dist(0, left1 - 1);
	int swap_position = uniform_dist(random_engine);
	std::cout << "sampled: " << swap_position;
	std::cout << '\n';

	std::vector<int> elements;
	std::vector<int>::iterator it;
	for (int i = 1; i < 10; i++) {
		elements.push_back(i);
	}
	//
	size_t left = std::distance(elements.begin(), elements.end());
	std::cout << left;
	std::cout << '\n';

	it = elements.begin();
	//std::cout << rand();
	std::vector<int>::iterator b = it;
	std::advance(b, rand() % left);
	std::swap(*it, *b);
	std::cout << *it;
	std::cout << '\n';

	std::cout << "myvector contains:";
	for (it = elements.begin(); it != elements.end(); it++) {
		 std::cout << ' ' << *it;
	}

	// using built-in random generator:
 	 http://www.cplusplus.com/reference/algorithm/random_shuffle/
	std::random_shuffle(elements.begin(), elements.end());
	std::cout << '\n';
	std::cout << "shuffled contains:";
	for (it = elements.begin(); it != elements.end(); it++) {
		 std::cout << ' ' << *it;
	}

	std::cout << '\n';
	*/

	// in case unordered set is not found in eclipse
	// http://stackoverflow.com/questions/17131744/eclipse-cdt-indexer-does-not-know-c11-containers
	std::unordered_set<std::string> stringSet;
	// inserting various string, same string will be stored
	// once in set
	stringSet.insert("code");
	stringSet.insert("in");
	stringSet.insert("c++");
	stringSet.insert("is");
	stringSet.insert("fast");

    std::string key = "slow";

    //  find returns end iterator if key is not found,
    //  else it returns iterator to that key
    if (stringSet.find(key) == stringSet.end())
    	std::cout << key << " not found\n\n";
    else
    	std::cout << "Found " << key << std::endl << std::endl;

    key = "c++";
    if (stringSet.find(key) == stringSet.end())
    	std::cout << key << " not found\n";
    else
    	std::cout << "Found " << key << std::endl;

    // now iterating over whole set and printing its
    // content
    std::cout << "\nAll elements : ";
    std::unordered_set<std::string> :: iterator itr;
    for (itr = stringSet.begin(); itr != stringSet.end(); itr++)
    	std::cout << (*itr) << std::endl;

	return 0;
}
