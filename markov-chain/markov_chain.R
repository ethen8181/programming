
# define state and transition matrix
states <- c('work', 'gym', 'pub', 'home')
transition <- matrix(
    c(0.2, 0.2, 0.2, 0.4,
      0.0, 0.1, 0.2, 0.7,
      0.0, 0.0, 0.5, 0.5,
      0.0, 0.0, 0.0, 1.0),
    byrow = TRUE, nrow = 4, 
    dimnames = list(states, states)
)
print(transition)

# matrix multiplication for three times
# we start with 1, 0, 0, 0, because we are current
# at work, and work is the first element of the state vector
start <- c(1, 0, 0, 0)
start %*% transition %*% transition %*% transition


library(markovchain)
# convert to a markov chain class first and
# perform the computation
mc <- new('markovchain', states = states, byrow = TRUE, 
          transitionMatrix = transition, name = 'daily routine')

start * mc ^ 3


states <- c('Rain', 'Nice', 'Snow')
transition <- matrix(
    c(0.50, 0.25, 0.25,
      0.50, 0.00, 0.50,
      0.25, 0.25, 0.50),
    nrow = 3, byrow = TRUE,
    dimnames = list(states, states)
)

# transition matrix after 6 steps
mc <- new('markovchain', states = states, byrow = TRUE, 
          transitionMatrix = transition, name = 'weather')
(mc ^ 6)@transitionMatrix

# steady state, the transition probability
# will remain the same
steady <- steadyStates(mc)
steady %*% transition

n <- nrow(transition)
Q <- t(transition) - diag(n)
Q[n, ] <- rep(1, n)
rhs <- c( rep(0, n - 1), 1)
PI <- solve(Q) %*% rhs
PI


