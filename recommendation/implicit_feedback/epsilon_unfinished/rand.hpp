#ifndef RAND_HPP_
#define RAND_HPP_

#include <vector>

template<class T>
std::vector<T> random_choice(std::vector<T>& indices, int n_random, int seed);

#endif /* RAND_HPP_ */