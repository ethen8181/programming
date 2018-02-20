from sklearn.base import BaseEstimator, ClassifierMixin
from scipy.sparse import csr_matrix
import numpy as np
from mlutils.models._fm import _sgd_update, _predict_instance


class FMClassifier(BaseEstimator, ClassifierMixin):
    """
    1. predict use sparse dot product
    2. summed use pointer and memset
    3. rename some variables
    4. hogwild for samples
    5. cache exp (gensim word2vec)
    """

    def __init__(self, n_factors = 10, n_iter = 3,
                 learning_rate = 0.01, random_state = 1234,
                 reg_w=0.0, reg_v=0.0, lambda_t=1.0, verbose = False):
        self.n_factors = n_factors
        self.n_iter = n_iter
        self.learning_rate = learning_rate
        self.verbose = verbose
        self.reg_w = reg_w
        self.reg_v = reg_v
        self.lambda_t = lambda_t
        self.random_state = random_state

    def fit(self, X, y):
        n_features = X.shape[1]
        self.w0 = 0.0
        self.w = np.zeros(n_features)

        # the factors are often initialized with a mean of 0 and standard deviation
        # of 1 / sqrt(number of latent factor specified)
        np.random.seed(self.random_state)
        scale = 1 / np.sqrt(self.n_factors)
        self.v = np.random.normal(scale = scale, size = (self.n_factors, n_features))

        y = y.copy().astype(np.int32)
        y[y == 0] = -1
        if not isinstance(X, csr_matrix):
            X = csr_matrix(X)

        history = []
        for _ in range(self.n_iter):  # pull the for loop outside
            loss = _sgd_update(X, y, self.w0, self.w, self.v, self.n_iter, self.n_factors,
                               self.learning_rate, self.reg_w, self.reg_v, self.lambda_t)
            history.append(loss)

        self.history = history
        return self

    def _predict(self, X):
        linear_output = np.dot(X, self.w)
        term = np.dot(X, self.v) ** 2 - np.dot(X ** 2, self.v ** 2)
        factor_output = 0.5 * np.sum(term, axis = 1)
        return self.w0 + linear_output + factor_output

    def predict_proba(self, X):
        pred = self._predict(X)
        pred_proba = 1.0 / (1.0 + np.exp(-pred))
        return pred_proba

    def predict(self, X):
        pred_proba = self.predict_proba(X)
        return pred_proba.round().astype(np.int)
