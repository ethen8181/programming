/*
 * rand.cpp
 *
 *  Created on: Apr 15, 2017
 *      Author: ethen
 */

#include "rand.hpp"
#include <vector>
#include <random>
#include <algorithm> // swap

/*
The intuition behind Fisher-Yates shuffling
http://eli.thegreenplace.net/2010/05/28/the-intuition-behind-fisher-yates-shuffling/

C++ : mt19937 Example
https://www.guyrutenberg.com/2014/05/03/c-mt19937-example/

Choose m elements randomly from a vector containing n elements
http://stackoverflow.com/questions/9345087/choose-m-elements-randomly-from-a-vector-containing-n-elements

Best way to extract a subvector from a vector?
http://stackoverflow.com/questions/421573/best-way-to-extract-a-subvector-from-a-vector
*/
template<class T>
std::vector<T> random_choice(std::vector<T>& indices, int n_random, int seed) {
    int n_random_copy = n_random;
    std::default_random_engine random_engine(seed);
    typename std::vector<T>::iterator start = indices.begin();
    size_t n_size = indices.size();
    while (n_random--) {
        typename std::vector<T>::iterator temp = start;
        std::uniform_int_distribution<int> uniform_dist(0, n_size - 1);
        int swap_position = uniform_dist(random_engine);
        temp += swap_position;
        std::swap(*start, *temp);
        ++start;
        --n_size;
    }

    std::vector<T> new_indices(indices.begin(), indices.begin() + n_random_copy);
    return new_indices;
}

// to prevent template linking error with the header file, explicitly state the type
// for the template
// https://isocpp.org/wiki/faq/templates#separate-template-fn-defn-from-decl
template std::vector<int> random_choice<int>(std::vector<int>& indices,
											 int n_random, int seed);
template std::vector<double> random_choice<double>(std::vector<double>& indices,
                                                   int n_random, int seed);
template std::vector<float> random_choice<float>(std::vector<float>& indices,
                                                 int n_random, int seed);


