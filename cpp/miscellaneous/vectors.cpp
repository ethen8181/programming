// http://www.codeguru.com/cpp/cpp/cpp_mfc/stl/article.php/c4027/C-Tutorial-A-Beginners-Guide-to-stdvector-Part-1.htm
// https://www.tutorialspoint.com/cplusplus/cpp_passing_arrays_to_functions.htm
// https://www.tutorialspoint.com/cplusplus/cpp_pointer_to_an_array.htm

#include <vector>
#include <iostream>

// if we wish to pass an array to a function,
// we need to declare it as array[] or array[size], or *array
double mean(double *array, size_t n) {
    double m = 0;
    for (size_t i = 0; i < n; i++) {
        m += array[i];
    }
    return m / n;
}

int main() {
    // an array name is a pointer to the first element of the array
    double ar[] = {1, 2, 3, 4, 5};
    std::cout << mean(ar, 5) << std::endl; // will print 3

    std::vector<double> a1;
    a1.push_back(1);
    a1.push_back(2);
    a1.push_back(3);
    a1.push_back(4);
    a1.push_back(5);
    std::cout << mean(&a1[0], 5) << std::endl; // will print 3


    // for bigger projects it can be tedious to repeatedly 
    // write out the explicit type of the vectors. and we
    // may use a typedef if we want
    typedef std::vector<int> int_vec_t;

    // To hold elements, vector will allocate some memory, 
    // mostly more than it needs. we can push_back() elements 
    // until the allocated memory is exhausted. 
    // Then, vector will trigger a reallocation and will grow the a
    // llocated memory block. This can mean that it will have to move 
    // (that means copy) the sequence into a larger block. 
    // And copying around a large number of elements can slow down our 
    // application dramatically. Note that the reallocation is absolutely 
    // transparent for us. we need to do nothing; vector will do all what that 
    // takes under the hood. Of course, there is something we can do to avoid 
    // having vector reallocate the storage too often

    // size_t is simply unsigned int in this case
    size_t size = 10;

    // make sure there's enough room for 10 integers
    // it will initialize them to the default value 0
    int_vec_t array1(size, 0);
    
    // do something with them:
    for(int i = 0; i < size; i++) {
        array1[i] = i;
    }
    std::cout << array1[1] << std::endl;


    // we can use iterators to loop through the elements
    std::vector<double> a2;
    std::vector<double>::const_iterator i;
    a2.push_back(1);
    a2.push_back(2);
    a2.push_back(3);
    a2.push_back(4);
    a2.push_back(5);
    for (i = a2.begin(); i != a2.end(); i++) {
        std::cout << *i << ',';
    }
    std::cout << std::endl;
    return 0;
}
