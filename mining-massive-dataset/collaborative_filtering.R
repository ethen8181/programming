# collaborative filtering 
# predicted unknown ratings of a utility matrix 

# example utility matrix, column represents items, rows represents users 
ratings <- c( 4, NA, 3, 5, NA, 5, 4, NA, 5, 4, 2, NA, 2, 4, NA, 3, 3, 4, 5, NA )
data <- matrix( ratings, nrow = 5, byrow = TRUE )

Sum  <- function(vector) sum( vector, na.rm = TRUE )
Mean <- function(vector) mean( vector, na.rm = TRUE )
Sd   <- function(vector) sd( vector, na.rm = TRUE )

# ----------------------------------------------------------------------------------
# [CenteredCosine] :
# normalize ratings by subtracting row means, before calculating cosine distance 
# a larger (positive) cosine implies a smaller angle and therefore a smaller distance 

CenteredCosine <- function( matrix, row1, row2 )
{
	ratings1 <- matrix[ row1, ]
	ratings1 <- ratings1 - Sum(ratings1) / length( na.omit(ratings1) )
	
	ratings2 <- matrix[ row2, ]
	ratings2 <- ratings2 - Sum(ratings2) / length( na.omit(ratings2) )

	cosine <- Sum( ratings1 * ratings2 ) / ( sqrt( Sum(ratings1^2) ) * sqrt( Sum(ratings2^2) ) )
	return(cosine)
}

# ----------------------------------------------------------------------------------
# [PredictRatings] : user - user recommendation 
# predict the specified user's (rows) ratings for specified item (columns)
# according to the kth nearest user
# hault if user has already ranked the item or the item has no ranking record
# produce warning if the number of users that rated the item is smaller than k
# and uses the maximum available number of users in the system to produce rating 

PredictRatings <- function( matrix = data, user = 2, item = 4, k = 2 )
{
	if( mean( is.na( matrix[ , item ] ) ) == 1 )
	{
		stop( "Cold start" )
	}else if( !is.na( matrix[ user, item ] ) )
	{
		stop( "The user has already ranked the item" )	
	}else  
	{
		similarity <- list()

		# obtain the centered cosine angle for between the specified user 
		# and all others who have given ratings to the user 
		for( i in 1:nrow(matrix) )
		{
			if( is.na( matrix[ i, item ] ) )
				similarity[[i]] <- NA
			else
				similarity[[i]] <- CenteredCosine( matrix, user, i )
		}
		similarity <- unlist(similarity)
		
		# given the cosine angle, use acos to convert back to degrees
		# the smaller the degrees the closer ( smaller )
		# acos returns the radian, multiply it by 180 and divide by pi to obtain degrees 
		degree <- acos(similarity) * 180 / pi
		
		# if the count of the rated item is smaller than the specified k
		# replace the specified k with the count
		rated <- sum( !is.na(degree) )
		if( rated < k )
		{
			k <- rated
			warning( "Number of user who rated this items is smaller than k" )
			warning( "Used ", as.character(rated), " to replace k" )
		}	
		# obtain the rows of the k-nearest distance, ties broken arbitrarily 
		nearest <- order( degree, na.last = TRUE )[1:k]

		# obtain the k smalleset centered cosine angle
		# and use it on the formula to compute ratings
		numerator   <- list()
		denominator <- list()		

		for( i in nearest )
		{
			# use character in list tp prevent adding null list to skiped index
			# weighted numerator : similarity * ( rating - average rating of that movie ) / standard deviation of the rating 
			numerator[as.character(i)] <- similarity[i] * ( ( matrix[ i, item ] - Mean( matrix[ i, ] ) ) / Sd( matrix[ i, ] ) )
			denominator[as.character(i)] <- abs(similarity[i])
		}
		
		# global baseline : average rating over all ratings in the system
		baseline <- Mean(matrix)
		# discrepancy between over all ratings and average of users ;
		# between over all ratings and average of that item 
		baseline <- baseline + ( Mean( matrix[user, ] ) - baseline ) + ( Mean( matrix[, item ] ) - Mean(matrix) )		

		# basline plus the formula 
		rating <- baseline + Sd( matrix[user,] ) * ( sum( unlist(numerator) ) / sum( unlist(denominator) ) )
	}
	return(rating)				
}

PredictRatings( data, user = 1, item = 2, k = 2 )



# --------------------------------------------------------------------------------------------------------------------
# Week 4 Quiz A, not related to above 

# -- Question 1 -----------------------------------------------------------------------
# Normalize the ratings by subtracting the average for each row and then 
# subtracting the average for each column in the resulting table

U <- matrix( c(1,2,3,4,5,2,3,2,5,3,5,5,5,3,2), nrow = 3, ncol = 5, byrow = TRUE )

U <- sweep( U, 1, rowMeans(U), "-" )
U <- sweep( U, 2, colMeans(U), "-" )

# Answer : The entry (B,M) is -1/3.


# -- Question 2 -----------------------------------------------------------------------
# The first five attributes are Boolean, and the last is an integer "rating." 
# Assume that the scale factor for the rating is α. Compute, as a function of α, 
# the cosine distances between each pair of profiles

library(proxy)

q2 <- matrix( c(1,0,1,0,1,2,1,1,0,0,1,6,0,1,0,1,0,2), nrow = 3, ncol = 6, byrow = TRUE )

# alpha <- .5
alpha <- 2
q2[ , ncol(q2) ] <- q2[ , ncol(q2) ] * alpha
rownames(q2) <- letters[1:3]

# define the distance between the two vectors for proxy 
# dot product of the two vectors divided by the procduct of the length the the two vectors
CosineDistance <- function( x, y )
{
    distance <- ( x %*% y ) / ( sqrt( sum( x^2 ) ) * sqrt( sum( y^2 ) ) )
    # returns the distance in degrees 
    return( acos(distance) * 180 / pi  )
}

# create a new entry in the registry
pr_DB$set_entry( FUN = CosineDistance, names = c("CosineDistance") )

# cosine degree distance matrix 
d <- dist( q2, method = "CosineDistance" )

# delete 
pr_DB$delete_entry( "CosineDistance" )

# Answer : False statement : For α = 0.5, C is closer to B than A is.
