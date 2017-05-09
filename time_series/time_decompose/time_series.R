setwd('/Users/ethen/Desktop/time_decompose')



# number of page view per days over a period of 103 weeks (almost 2 years)
library(data.table)
web_data <- fread('webTraffic.csv')


set.seed(4)
data <- read.csv("webTraffic.csv", sep = ",", header = T)
days <- as.numeric(web_data$Visite)
plot(as.ts(days))
for (i in 1:45) {
 pos = floor(runif(1, 1, 50))
 days[i*15+pos] = days[i*15+pos]^1.2
}
days[510+pos] = 0
