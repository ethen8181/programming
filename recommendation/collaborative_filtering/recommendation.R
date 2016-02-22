
library(data.table)
setwd("/Users/ethen/Desktop/recommendation")

fulldf <- fread("bigdf.csv")

smalldf <- fulldf[ user_review_count > 60 & business_review_count > 150, ]


user <- smalldf[ , .( mean = mean(stars),
			  	   	  count = .N ), by = 'user_id' ]
merge( smalldf, user, by = "user_id", sort = FALSE )

smalldf[ , .( mean = mean(stars),
			  count = .N ), by = 'business_id' ]


