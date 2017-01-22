import numpy as np
import multiprocessing
from tqdm import tqdm
from sklearn.base import BaseEstimator
from implicit._implicit import least_squares

class ALS(BaseEstimator):
    """
    Inherit scikit-learn's BaseEstimator to get some free stuff
    - class representations, more informative when printing class
    - get, set parameters (it will raise ValueError if we pass in
      illegal parameters, while setattr will simply let it through)
    """
    def __init__(self, reg = 0.01, seed = 1234, alpha = 15,
                 n_iters = 15, n_factors = 20, n_jobs = -1, verbose = True):
        self.reg = reg
        self.seed = seed
        self.alpha = alpha
        self.n_jobs = n_jobs
        self.n_iters = n_iters
        self.verbose = verbose
        self.n_factors = n_factors

    def fit(self, ratings):
        """
        Fit an alternating least squares model
        
        Parameters
        ----------
        ratings : scipy sparse csr_matrix, shape = (n_users, n_items) 
            sparse matrix of user-item interactions
        """
        # create confidence matrix
        Cui = ratings.copy()
        Cui.data *= self.alpha
        Ciu = Cui.T.tocsr()
        self.n_users, self.n_items = Cui.shape

        # initialize (user/item) latent vectors randomly with a set seed
        rstate = np.random.RandomState(self.seed)
        self.user_vecs = rstate.normal(size = (self.n_users, self.n_factors))
        self.item_vecs = rstate.normal(size = (self.n_items, self.n_factors))

        # progress bar for training iteration if verbose is turned on
        loop = range(self.n_iters)
        if self.verbose:
            loop = tqdm(loop, desc = self.__class__.__name__)

        # set the acutal cpu (thread) that will be used
        n_jobs = multiprocessing.cpu_count()
        if self.n_jobs > 0 and self.n_jobs < n_jobs:
            n_jobs = self.n_jobs
        
        for _ in loop:
            least_squares(Cui, self.user_vecs, self.item_vecs, self.reg, n_jobs)
            least_squares(Ciu, self.item_vecs, self.user_vecs, self.reg, n_jobs)
        
        # to avoid re-computation at predict
        self._predicted = False
        return self

    def predict(self):
        """
        predict ratings for every user and item,
        the result will be cached to avoid re-computing 
        it every time we call predict, thus there will
        only be an overhead the first time we call it
        """
        if not self._predicted:
            self._get_prediction()
            self._predicted = True

        return self._pred

    def _get_prediction(self):
        """predicted ratings (dot product of user and item vectors)"""
        self._pred = self.user_vecs.dot(self.item_vecs.T)
        return self

