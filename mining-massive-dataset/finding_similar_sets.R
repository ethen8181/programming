# Mining Massive Datasets Quiz for Week 2
# LSH Basics
library(data.table)
library(MASS)


# -- Question 4 --------------------------------------------------------------------------
# Find the set of 2-shingles for the document "ABRACADABRA" and "BRICABRAC"
# Answer the following questions
# 1. How many 2-shingles does the two documents have?
# 2. How many 2-shingles do they have in common?
# 3. What is the Jaccard similarity between the two documents"?

document1 <- "ABRACADABRA"
document2 <- "BRICABRAC"

# [Shingling]: returns a vector listing the k-shingle of a given document, k default as 2 
Shingling <- function( document, k = 2 )
{
	shingles <- vector()
	for( i in 1:nchar(document) )
	{
		if( i + k - 1 > nchar(document) )
			break
		shingles[i] <- substring( document, i, i + k - 1 )
	}
	# include the duplicates only once
	shingles <- unique(shingles)
	return(shingles)	
}

# [JaccardSimilarity]: Given two k-shingles
# returns the union, intersect and jaccard similarity as a list
JaccardSimilarity <- function( x, y )
{
	set_intersection <- length( intersect( x, y ) )
	set_union <- length( union( x, y ) )
	
	list( union        = set_union, 
		  intersection = set_intersection, 
		  jaccard      = fractions( set_intersection / set_union ) )
}


shingles1 <- Shingling( document1 ) ; length(shingles1)
shingles2 <- Shingling( document2 ) ; length(shingles2)
# both documents have 7 2-shingles

JaccardSimilarity( shingles1, shingles2 )
# Answer : The Jaccard similarity is 5/9



# -- Question 5 --------------------------------------------------------------------------
# Suppose we want to assign points to whichever of the points (0,0) or (100,40) is nearer. 
# Which point will be assigned to (0,0) when the L1 norm is used, 
# but assigned to (100,40) when the L2 norm is used

data <- read.csv(
	text = "0,0
		    100,40",
    header = FALSE
)

# [CalculateDistance]: returns a data frame specifying the distance between the 
# new given datapoint and each point in the original data.   
# @measures  = L2 for Euclidean distance, L1 for manhattan distance
CalculateDistance <- function( datapoint, data = data, measures = "L2" )
{
	distance <- data.frame()
	if( measures == "L1" )
	{
		for( i in 1:nrow(data) )
			distance[ i, 1 ] <- sum( abs( datapoint - data[i,] ) )
	}

	if( measures == "L2" )
	{
		for( i in 1:nrow(data) )
			distance[ i, 1 ] <- sqrt( sum( ( datapoint - data[i,] ) ^2 ) )
	}
	setnames( distance, "dist" )
	return(distance)		
}

datapoint <- c( 51, 18 ) 
distance_L1 <- CalculateDistance( datapoint, data, "L1" )
distance_L2 <- CalculateDistance( datapoint, data, "L2" )

(distance_L1[1,] < distance_L1[2,]) & ( distance_L2[1,] > distance_L2[2,] )
# Answer : (51,18) 

