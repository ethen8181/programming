import copy
import numpy as np
from tqdm import tqdm
from itertools import product

class GridSearch:

    def __init__(self, base_model, params_opt, scorer, verbose = True):
        self.scorer = scorer
        self.verbose = verbose
        self.base_model = base_model
        self.params_opt = params_opt

    def fit(self, ratings, user_index, eval_set = None):
        self.best_score = -np.inf
        for params in self._get_params_grid():
            current_model = copy.deepcopy(self.base_model)
            current_model.set_params(**params)
            current_model.fit(ratings)
            
            # best model will be determined by th performance of 
            # the validation set instead of the train if one is given
            if eval_set:
                validation = eval_set
            else:
                validation = ratings

            score = self.scorer(current_model, validation, user_index)
            if self.best_score < score:
                self.best_score = score
                self.best_params = params
                self.best_estimator = current_model

        return self

    def _get_params_grid(self):
        """
        grid search, create cartesian product of the parameters'
        options, this will be a generator that will allow us to loop
        through all possible parameter combinations, note if we want to
        expand this to cross validation we'll have to turn it into a list,
        or else the generator will be exhausted at the first fold
        """
        # for reproducibility, always sort the keys of a dictionary
        items = sorted(self.params_opt.items())
        
        # unpack parameter and the range of values
        # into separate list; then unpack the range 
        # of values to compute the cartesian product
        # and zip it back to the original key
        key, value = zip(*items)
        cartesian = product(*value)
        for v in cartesian:
            params = dict(zip(key, v))
            yield params

    def predict(self):
        return self.best_estimator.predict()

