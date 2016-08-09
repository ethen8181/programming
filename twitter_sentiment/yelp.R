
library(ggplot2)
library(tidytext)
library(wordcloud)

library(readr)
library(jsonlite)
library(data.table)



library(dplyr)

# we're reading only 200,000 in this example
# you can try it with the full dataset too, it's just a little slower to process!
setwd('/Users/ethen/programming/twitter_sentiment/yelp_dataset_challenge_academic_dataset')
infile <- 'yelp_academic_dataset_review.json'
review_lines <- read_lines( infile, n_max = 200000, progress = FALSE )



review_combined <- paste( '[', paste( review_lines, collapse = ', ' ), ']' )
reviews <- data.table( jsonlite::fromJSON( review_combined, flatten = TRUE ) )

