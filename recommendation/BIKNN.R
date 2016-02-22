library(proxy)
library(Matrix)
library(data.table)
setwd("/Users/ethen/Desktop")

# don't read in the fourth column, timestamp
data_train <- fread( "u1.base", select = 1:3 )
setnames( data_train, c( "userID", "itemID", "ratings" ) )

# note that the rows are items and the columns are user
rating_mat <- with( data_train,
                    sparseMatrix( i = itemID, j = userID, x = ratings ) )

ItemBase <- function( x, y )
{
    # index <- intersect(  which( !is.na(x) ), which( !is.na(y) ) )
    
    # NA ratings is stored as 0
    index <- intersect(  which( x != 0 ), which( y != 0 ) )
    x <- x[ index ]
    y <- y[ index ]
    
    # check to avoid zero denominators
    if( length(index) > 0 )
    {
        similarity <- sum( x * y ) / ( sum(x^2) + sum(y^2) )
        return(similarity)
    }else
        return(0)
}

pr_DB$set_entry( FUN = ItemBase, names = "ItemBase" )
similarity_mat <- dist( as.matrix(rating_mat), method = "ItemBase" )
pr_DB$delete_entry("ItemBase")

as.matrix(similarity_mat)