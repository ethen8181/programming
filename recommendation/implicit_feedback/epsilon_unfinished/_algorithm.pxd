from libcpp.vector cimport vector

cdef extern from "rand.hpp" nogil:
    vector[T] random_choice[T](vector[T]& indices, int n_random, int seed)
