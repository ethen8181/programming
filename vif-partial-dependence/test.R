library(ISLR)
library(randomForest)
library(dplyr)

# set seed for reproducibility
set.seed(42)
data(College)
rf <- randomForest(Grad.Rate ~ ., data = College)
# varImpPlot(rf)
# partial plots from random forest
par(mfrow = c(2 ,4)) 
for (i in 1:8) {
    partialPlot(rf, 
				pred.data = College, 
				x.var = names(College)[2],
				xlab = names(College)[2])
}


rf$type




test <- function(data, xname) {

    target <- data[, xname]

    if (is.factor(target)) { # categorical values
        x_points <- levels(target)
        y_points <- numeric(length(x_points))

        for (i in seq_along(x_points)) {
            x_data <- data
            x_data[, xname] <- factor(x_points[i], levels = x_points)
            y_pred <- predict(rf, newdata = x_data)
            y_points[i] <- mean(y_pred)
        }
    } else {
        # for numeric values, generate a fix number of values
        # in between the min and max value of the target column
        n_points <- min(length(unique(target)), 50)
        x_points <- seq(min(target), max(target), length = n_points)
        y_points <- numeric(length(x_points))

        for (i in seq_along(x_points)) {
            x_data <- data
            x_data[, xname] <- x_points[i]
            y_pred <- predict(rf, newdata = x_data)
            y_points[i] <- mean(y_pred)
        }
    }

    invisible(list(x = x_points, y = y_points))
}
data <- College
xname <- names(College)[1]
points <- test(College, xname)

barplot(points$y)
plot(points$x, points$y, type = "l")



    for (i in seq_along(x_points)) {
        x_data <- data
        x_data[, xname] <- x_points[i] rep(x.pt[i], n)
        if (classRF) {
            pr <- predict(x, x.data, type = "prob")
            y.pt[i] <- weighted.mean(log(ifelse(pr[, focus] == 0,
                                                .Machine$double.eps, pr[, focus]))
                                     - rowMeans(log(ifelse(pr == 0, .Machine$double.eps, pr))),
                                     w, na.rm=TRUE)
        } else {
            y.pt[i] <- weighted.mean(predict(x, x.data), w, na.rm=TRUE)
        }
    }


}

test(College, xname)


var1_vals <- seq(from = min(College$Outstate),
                 to = max(College$Outstate),
                 by = (max(College$Outstate) - 
                         min(College$Outstate))/19)

var2_vals <- seq(from = min(College$perc.alumni),
                 to = max(College$perc.alumni),
                 by = (max(College$perc.alumni) - 
                         min(College$perc.alumni))/19)

marginalPlot()