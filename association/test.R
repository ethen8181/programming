library(arules)
library(arulesViz)
library(data.table)

filepath <- file.path( 'programming', 'association' )
setwd(filepath)


?discretize

# --------------------------------------------------------------------------

# inspect the generated rules, which returns a data.frame
# including the left/right hand side, support, confidence and lift
inspect( head(rules) )

# we can sort the rules
rules_sorted <- arules::sort( rules, by = 'lift' )
inspect( head(rules) )


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



if(!file.exists('SQF_Codebook.pdf')) {
    
}

if( !file.exists('SQF 2012.csv') ) {
    download.file( 'http://www.nyclu.org/files/SQF_Codebook.pdf', 'SQF_Codebook.pdf' )
    download.file( 'http://www.nyclu.org/files/stopandfrisk/Stop-and-Frisk-2012.zip',
                   'Stop-and-Frisk-2012.zip' )
    unzip('Stop-and-Frisk-2012.zip')
}


