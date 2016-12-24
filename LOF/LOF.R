# http://www.rdatamining.com/examples/outlier-detection

library(Rlof)
outlier_scores <- Rlof::lof( iris[, -5], k = 5 )

# order is essentially argument sort,
# thus the first element will be the argument
# that has the highest score (sorted by decreasing order)
order(outlier_scores, decreasing = TRUE)

# then we have to choose the cutoff score
