cimport cython
cimport _algorithm
from libc.math cimport ceil
from libcpp.vector cimport vector
from cython.parallel import parallel, prange

# TODO:
# could not get fused type vector to work;
# the input to random choice should be
# able to work for all integer, float and double
# ctypedef fused vector_t:
#     vector[cython.int]
#     vector[cython.float]
#     vector[cython.double]


# cdef inline vector[int] random_choice(vector[int]& indices, 
#                                       int n_random, int seed) nogil:
#     return _algorithm.random_choice(indices, n_random, seed)

cpdef vector[int] random_choice(vector[int]& indices, 
                                      int n_random, int seed):
    return _algorithm.random_choice(indices, n_random, seed)

# cpdef _create_train_test(double[:, :] ratings, double test_size, int seed):
#     cdef:
#         #int[:] split_index, 
#         int[:] indptr = ratings.indptr, indices = ratings.indices
#         int n_users = ratings.shape[0]
#         int u = 0, index, n_splits
        
#         vector[int] row, col, split_index, test_index
#         int i

#     with nogil, parallel(num_threads = 7):
#         for u in prange(n_users, schedule = 'guided'):
            
#             for index in range(indptr[u], indptr[u + 1]):
#                 split_index.push_back(indices[index])
            
#             n_splits = <int>ceil(test_size * split_index.size())
#             test_index = random_choice(split_index, n_splits, seed)
#             for i in range(n_splits):
#                 row.push_back(u)
#                 col.push_back(test_index[i])

#     return row, col


