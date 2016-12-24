# Mining Massive Datasets Quiz for Week 1
# pagerank

# Define Function 
# -----------------------------------------------------------------------------------
# [AdjacencyMatrix] : Convert the edge list to adjacency matrix.

AdjacencyMatrix <- function( edgelist )
{
	# initialize the matrix
	A <- matrix( 0, n, n )

	# set the edges for the matrix
	for( i in 1:nrow(edgelist) )
	{
		A[ edgelist[ i, "tail" ], edgelist[ i, "head" ] ] <- 1
	}
	return(A)
}

# -----------------------------------------------------------------------------------
# [StochasticMatrix] : Convert the adjacency matrix to column-wise stochastic,
# where the sum of each column entry sums to 1.
# @taxation = boolean value, indicating to include the random uniform teleport or not 
# @damping  = damping threshold, value between 0 ~ 1, probability that it will follow the outlinks
# will not play any role if taxation is set to FALSE

StochasticMatrix <- function( matrix, taxation = TRUE, damping = .85 )
{
	sum_of_columns <- colSums(matrix)

	# if the graph have dead ends, that is column entry's sum equals 0, 
	# add the uniform random teleport 
	# assign 1 to every row of that column 
	# and assign the row(or column) number of the matrix to its sum of columns
	if( 0 %in% sum_of_columns )
	{
		dead_ends <- which( sum_of_columns == 0 )
		matrix[ , dead_ends ] <- 1
		sum_of_columns[ dead_ends ] <- nrow(matrix)
	}	
	
	if(taxation)
	{
		# initialize the teleport matrix
		A <- matrix( ( 1-damping ) / n, n, n )
		# sweep : apply the function to each element in each column 	
		A <- A + damping * sweep( matrix, 2, sum_of_columns, "/" )
	}else
		A <- sweep( matrix, 2, sum_of_columns, "/" )	
	return(A)	
}

# -----------------------------------------------------------------------------------
# [ComputeEigenvalue]: Computes the pagerank of a given column-wise stochastic matrix
# using the eigen values and vectors way, 
# choose the first vector, and use Re to return the real value part.
# @normalize = sum of the page rank vector 

ComputeEigenvalue <- function( matrix, normalize = 1 )
{
	value <- Re( eigen(matrix)$vectors[ ,1 ] )

	# normalize the page rank values
	pageranks <- ( value / sum(value) ) * normalize
	pageranks	
}

# -----------------------------------------------------------------------------------
# [PowerIteration]: Computes the pagerank of a given column-wise stochastic matrix
# using power iteration 
# @epsilon = threshold value, the iteration will hault once the difference between the 
# value of the new vector and the vector in the previous iteration is smaller than this number

PowerIteration <- function( matrix, epsilon = .0005 )
{
	# the initializing vector can be random
	start_vector <- rep( 1 / nrow(matrix), nrow(matrix) )

	# initialize the new vector as null, serves as the starting condition for the while loop
	new_vector <- NULL
	# stop the iteration when the sum of the absolute difference is smaller then the epsilon value 
	while( is.null(new_vector) | sum( abs( new_vector - start_vector ) ) > epsilon )
	{
		new_vector <- start_vector
		start_vector <- matrix %*% new_vector
	}	
	return(start_vector)
}


# -- Question 1 -------------------------------------------------------------------------
# PageRank with a β of 0.7, and the sum of the three pages' pagerank must be 3
# graph 
# A > B
# A > C
# B > C
# C > C


quiz1 <- read.csv( 
	text = "1,2
			1,3
			2,3
			3,3",			
	header = FALSE
)
names(quiz1) <- c( "head", "tail" )
quiz1

# obtain maximum number to determine the rows and columns for the squared matrix
n <- max( apply( quiz1, 2, max ) )

quiz1_matrix <- AdjacencyMatrix(quiz1)
quiz1_matrix <- StochasticMatrix( quiz1_matrix, damping = .7 )
ComputeEigenvalue( quiz1_matrix, normalize = 3 )
# Answer : A + C = 2.595


# -- Question 2 -------------------------------------------------------------------------
# Compute PageRank with β=0.85
# graph
# A > B
# A > C
# B > C
# C > A

quiz2 <- read.csv( 
	text = "1,2
			1,3
			2,3
			3,1",			
	header = FALSE
)
names(quiz2) <- c( "head", "tail" )
quiz2

n <- max( apply( quiz2, 2, max ) )

quiz2_matrix <- AdjacencyMatrix(quiz2)
quiz2_matrix <- StochasticMatrix(quiz2_matrix)
pageranks <- ComputeEigenvalue(quiz2_matrix)

# equivalent as using the page.rank function from the igraph package 
library(igraph)
quiz2_matrix <- AdjacencyMatrix( quiz2 )
# transpose to row-wise stochastic matrix for the graph.adjacency function 
graph <- graph.adjacency( t(quiz2_matrix), mode = "directed", diag = TRUE )
# default damping is set to .85 
page.rank(graph)

# Answer : .95B = .475A + .05C

# -- Question 3 ---------------------------------------------------------------------
# Using the graph from question 2
# Assuming no "taxation", use the power iteration to compute the pagerank 
# starting with the "0th" iteration where all three pages have rank a = b = c = 1
# Pagerank at the 5th iteration

n <- max( apply( quiz2, 2, max ) )
quiz3_matrix <- AdjacencyMatrix( quiz2 )
quiz3_matrix <- StochasticMatrix( quiz3_matrix, taxation = FALSE )

start <- rep( 1, nrow(quiz3_matrix) )
for (i in 1:5) start <- quiz3_matrix %*% start

library(MASS)
fractions(start)

# Answer : After iteration 5, b = 5/8

# testing code
# the two method produces similar results 
ComputeEigenvalue(quiz3_matrix)
PowerIteration(quiz3_matrix)



