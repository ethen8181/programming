# http://blog.h2o.ai/2016/06/hyperparameter-optimization-in-h2o-grid-search-random-search-and-the-future/
# library(devtools)
# install_github("h2oai/h2o-3/h2o-r/ensemble/h2oEnsemble-package")
library(h2o)
library(readr)
library(data.table)
library(h2oEnsemble)
setwd('/Users/ethen/Desktop')
write_csv(iris, 'iris.csv')

h2o.init(nthreads = -1)
# h2o.no_progress()
# h2o.show_progress()
data <- h2o.uploadFile(path = 'iris.csv', destination_frame = 'data')

# train/valid/test split
splits <- h2o.splitFrame( data, ratios = c(0.6, 0.2), seed = 1234 )
X_train <- h2o.assign( splits[[1]], 'X_train' ) 
X_val <- h2o.assign( splits[[2]], 'X_val' )
X_test <- h2o.assign( splits[[3]], 'X_test' )

# specify the response and predictor columns
y <- 'Species'
x <- setdiff( colnames(train), y )

# the random search criteria and nfolds
# is applicable for all models
nfolds <- 2
stopping_metric <- 'misclassification'
stopping_tolerance <- 0.05
stopping_rounds <- 5
search_criteria <- list(
    strategy = 'RandomDiscrete', 
    stopping_metric = stopping_metric, 
    stopping_tolerance = stopping_tolerance, 
    stopping_rounds = stopping_rounds
)

# gbm's random search hyperparameters;
# max depth and sample rate (row sample rate per tree)
# are also applicable for random forest
max_depth_opt <- 4:15
sample_rate_opt <- seq(from = 0.7, to = 1, by = 0.05) - 0.01
col_sample_rate_opt <- seq(from = 0.7, to = 1, by = 0.05) - 0.01

gbm_params_opt <- list(
    max_depth = max_depth_opt, 
    sample_rate = sample_rate_opt,
    col_sample_rate = col_sample_rate_opt
)

rs_gbm <- h2o.grid(
    algorithm = 'gbm',
    grid_id = 'rs_gbm',
    x = x, 
    y = y,
    training_frame = train,
    nfolds = nfolds,
    
    # if we are to use the stacking functionality,
    # all the base models have to use fold_assignment = 'Modulo'
    fold_assignment = 'Modulo',
    ntrees = 300,
    balance_classes = TRUE,
    stopping_metric = stopping_metric, 
    stopping_tolerance = stopping_tolerance, 
    stopping_rounds = stopping_rounds,
    hyper_params = gbm_params_opt,
    search_criteria = search_criteria
)


# random forest's random search hyperparameters
rf_params_opt <- list(
    max_depth = max_depth_opt, 
    sample_rate = sample_rate_opt
)

rs_rf <- h2o.grid(
    algorithm = 'randomForest',
    grid_id = 'rs_rf',
    x = x, 
    y = y,
    training_frame = train,
    nfolds = nfolds,
    fold_assignment = 'Modulo',
    ntrees = 300,
    balance_classes = TRUE,
    stopping_metric = stopping_metric, 
    stopping_tolerance = stopping_tolerance, 
    stopping_rounds = stopping_rounds,
    hyper_params = rf_params_opt,
    search_criteria = search_criteria
)


# deep learning hyperparameter
hidden_opt <- list( c(64, 64, 64, 64) )

# the number of dropout ratios has to match the number of hidden layers
# http://stackoverflow.com/questions/39212635/how-to-tune-hidden-dropout-ratios-in-h2o-grid-in-r
dropout <- seq(from = 0.1, to = 0.5, by = 0.05)
hidden_dropout_ratios_opt <- lapply( dropout, function(dropout_ratio) {
    rep( dropout_ratio, length(hidden_opt[[1]]) )
})
l2_opt <- c(0.5, 0, 0.1, 0.01)

dl_params_opt <- list(
    hidden = hidden_opt,
    
    # controls dropout between input layer and the first hidden layer
    # it's exactly the same thing as dropping rows from the training process
    input_dropout_ratio = sample_rate_opt,
    hidden_dropout_ratios = hidden_dropout_ratios_opt,
    l2 = l2_opt
)

rs_dl <- h2o.grid(
    algorithm = 'deeplearning',
    grid_id = 'rs_dl',
    x = x, 
    y = y,
    training_frame = train,
    epochs = 200,
    
    # Rectifier activation is simply Relu
    activation = 'RectifierWithDropout',
    nfolds = nfolds,
    fold_assignment = 'Modulo',
    stopping_metric = stopping_metric, 
    stopping_tolerance = stopping_tolerance, 
    stopping_rounds = stopping_rounds,
    hyper_params = dl_params_opt,
    search_criteria = search_criteria
)


# obtain all the randomforest, gbm, deeplearning models and stack them together
# with a user specified metalearner
models_gbm <- lapply( rs_gbm@model_ids, function(model_id) h2o.getModel(model_id) )
models_rf <- lapply( rs_rf@model_ids, function(model_id) h2o.getModel(model_id) )
models_dl <- lapply( rs_dl@model_ids, function(model_id) h2o.getModel(model_id) )
models <- c(models_gbm, models_rf, models_dl)

# it's always a good idea to try a GLM restricted to non-negative weights as a metalearner
# there have been a lot of empircal studies that show that non-negative weights can 
# lead to better performance
metalearner <- function(..., non_negative = TRUE) {
    h2o.glm.wrapper(..., non_negative = non_negative)
}

model_stack <- h2o.stack(
    models = models, 
    response_frame = train[, y],
    metalearner = metalearner
)

h2o.save_ensemble(fit, path = "./h2o-ensemble-model-savetest")


# sort the model by the specified evaluation metric
# and obtain the top one (the best model)
rs_rf_sorted <- h2o.getGrid(
    grid_id = 'rs_rf', 
    sort_by = 'accuracy', 
    decreasing = TRUE
)
best_model <- h2o.getModel(rs_rf_sorted@model_ids[[1]])
dt_predict <- as.data.table( h2o.predict(best_model, test) )

h2o.shutdown()





