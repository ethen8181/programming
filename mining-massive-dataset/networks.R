# Mining Massive Datasets Quiz for Week 3


library(igraph)
library(stringr)

# -- Question1 ------------------------------------------------------------------------
# Construct the adjacency matrix A, the degree matrix D, and the Laplacian matrix L
# from the adjaceny list below 
# Then identify the true statement from the list below

# read in the adjacency list data  
data1 <- read.csv(

	text = "A,C,F
			B,E,H
			C,A,D,F
			D,C,E,G
			E,B,D,H
			F,A,C,G
			G,D,F,H
			H,B,E,G",
	header = FALSE,
	stringsAsFactors = FALSE
)

# preprocessing : strim the white spaces 
data1 <- data.frame( sapply( data1, str_trim ) )

# match the letters with its corresponding index
# [LetterToNumbers] : convert the original letter dataframe to index
# e.g. A gets convert to 1, C to 3 etc.
LetterToNumbers <- function( df )
{
	df <- sapply( df, function(x)
	{
		# use LETTERS for capital letters 
		match( x, LETTERS )
	})
	return(df)
} 
data1 <- LetterToNumbers(data1)

# [AdjacencyList] : convert the index data frame to a adjacency list 
AdjacencyList <- function( df )
{
	adj_list <- list()
	for( i in 1:nrow(df) )
	{
		row <- df[ i, complete.cases( df[i,] ) ]
		adj_list[[ row[1] ]] <- row[ 2:length(row) ] 
	}
	return( adj_list )	
}
adj_list <- AdjacencyList(data1)

# convert the list to a igraph adjacency list type 
graph_list <- graph.adjlist(adj_list)

# calculate the sum of the degree 
sum( degree( graph_list, mode = "out" ) )
# Answer : The sum of the entries of D is 22.

# testing code, not-related
# obtain the matrix, represented as a sparse matrix
# you can use as.matrix to convert to normal matrix 
get.adjacency(graph_list)


# -- Question2 ------------------------------------------------------------------------
# The goal is to find two clusters in this graph using Spectral Clustering on the Laplacian matrix. 
# Compute the Laplacian of this graph and the 2nd eigenvector of the Laplacian 
# (the one corresponding to the 2nd smallest eigenvalue).
# To cluster the points, we decide to split at the mean value. We say that a node is a tie 
# if its value in the eigen-vector is exactly equal to the mean value. 
# Let's assume that if a point is a tie, we choose its cluster at random. 
# Identify the true statement from the list below.

# edge list data
data2 <- read.csv(

	text = "1,2
			1,3
			2,1
			2,4
			2,6
			3,1
			3,4
			4,2
			4,3
			4,5
			5,4
			5,6
			6,2
			6,5",
	header = FALSE,
)
names(data2) <- c( "tail", "head" )

edge_list <- graph.data.frame( data2 )
laplacian <- graph.laplacian(edge_list)

# second smallest eigenvalue's eigenvectors 
# after obtaining the eigenvectors you can choose to split the graph accordingly

eigen_vector <- eigen(laplacian)$vector[ , 5 ]
eigen_vector > mean(eigen_vector)

# visualize the eigen vector, and the splitting point 
library(ggplot2)
ggplot( data.frame( n = 1:length(eigen_vector), v = eigen_vector), aes( n, v ) ) + 
geom_point() + 
geom_line() + 
geom_hline( yintercept = mean(eigen_vector), color = "blue" )

# Answer : 2 is a tie




