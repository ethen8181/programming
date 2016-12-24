# Multinomial case not yet supported in H2O Ensemble


# library(devtools)
# install_github("h2oai/h2o-3/h2o-r/ensemble/h2oEnsemble-package")
library(h2oEnsemble)

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

