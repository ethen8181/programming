
# lots of naturally parallel problem
# think about independent tasks (hint: 
# computational expensive for loops for a great place to start)


# pitfalls:
# resource contention, we want to be
# parallelizing tasks to match our resources,
# e.g. we have multiple CPU, thus ideally we want
# to parallelize things that is going to use the CPU
# not something like reading/writing to disk/database
# since we usually only have 1 of them. And our different
# parallel tasks will be contending and fighting for that
# one shared resources
# overhead, thrashing,


# common operation: map

# M = function(item) ...

# map(M, items) = function(item1), function(item2)



# avoid modifying global state

# item_id = [0, 0, 0, 0]
# parallel for each(i = 1:4) {
# 	item_id[i] = 1
# }


# cross validation, easily parallelizable
# grid search, random forest

library(doParallel)

n_cores <- detectCores()
n_cores

test <- function(i) {
    summary( rnorm(100000) )
}

# the time difference between using n_cores
inputs <- 1:20
system.time({
    results <- mclapply(inputs, test, mc.cores = n_cores)
})

system.time({
    results <- lapply(inputs, test)
})


# overhead,
# sending tasks out to another process and have work to be done
# there takes some time and there's some work involved, thus
# we don't want to parallelizing things that already runs really
# fast in sequence, especially in R where some functions can be
# vectorized
system.time({
    results <- mclapply(1:10000, sqrt, mc.cores = n_cores)
})

system.time({
    results <- lapply(1:10000, sqrt)
})


lapply( icount(100), function(x) {
    print(x)
})


# http://www.exegetic.biz/blog/2013/11/iterators-in-r/


