library(arules)
library(data.table)
setwd('/Users/ethen/programming/association')

load('titanic.raw.rdata')
dt <- data.table(titanic.raw)

# apriori takes a transaction class data or any data format that 
# can be transformed to it (e.g. data.frame or matrix),
# and a parameter argument that takes a list of arguments to specify
# the parameter for the algorithm
rules <- apriori( 
	dt,

	# the min/max len denotes the min/max number of items in a itemset
	parameter = list( support = 0.1, confidence = 0.5, minlen = 1, maxlen = 5 ),

	# don't print the algorthm's training message
	control = list( verbose = FALSE )
)

# inspect the generated rules, which returns a data.frame
# including the left/right hand side, support, confidence and lift
inspect( head(rules) )

# for appearance we can specify we only want rules with rhs 
# containing "Survived" only (we then specfiy the default parameter for all
# the other items that are not expliciting specified)
rules <- apriori( 
	dt,
	parameter = list( support = 0.1, confidence = 0.5, minlen = 1, maxlen = 5 ),
	appearance = list( rhs = c( 'Survived=No', 'Survived=Yes' ), default = 'lhs' ),
	control = list( verbose = FALSE )
)

# we can sort the rules
rules_sorted <- arules::sort( rules, by = 'lift' )
inspect(rules_sorted)


inspect(rules_sorted[1:2])
# Rule #2 is a redudant rule since it provides no extra knowledge
# in addition to rule #1, which already tells us that all 2nd-class children 
# survived.

# find redundant rules and prune them
subset_matrix <- is.subset( rules_sorted, rules_sorted )
subset_matrix[ lower.tri( subset_matrix, diag = TRUE ) ] <- NA
redundant <- colSums( subset_matrix, na.rm = TRUE ) >= 1
which(redundant)

rules_pruned <- rules_sorted[!redundant]
inspect(rules_pruned)


library(arulesViz)
plot(rules_pruned)

# convert to data.table and remove the '=>' column that
# is generated during the process (named V2)
library(DT)
rules_info <- data.table( inspect(rules_pruned) )
rules_info[ , V2 := NULL ]
DT::datatable(rules_info)




library(cowplot)
library(ggplot2)

# a scatter plot using support and confidence on the x and y axes. 
# In addition a lift is used as the color of the points
ggplot( rules_info, aes( support, confidence, color = lift ) ) + 
geom_point() + 
labs( title = sprintf( 'scatter plot for %d rules', nrow(rules_info) ) )



