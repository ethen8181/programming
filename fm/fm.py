import numpy as np
from sklearn.base import BaseEstimator, RegressorMixin


class FMDenseClassification(BaseEstimator, RegressorMixin):
    """
    Factorization machines implementation using SGD
    (Stochastic Gradient Descent) optimizer.

    References
    ----------
    Factorization Machines http://www.csie.ntu.edu.tw/~b97053/paper/Rendle2010FM.pdf
    """

    def __init__(self, n_iter = 30, learning_rate = 0.01, n_factors = 10,
                 reg_w = 0.1, reg_v = 0.1, random_state = 1234):
        self.reg_w = reg_w
        self.reg_v = reg_v
        self.n_iter = n_iter
        self.n_factors = n_factors
        self.random_state = random_state
        self.learning_rate = learning_rate

    def fit(self, X, y):
        # check input matrix
        n_samples, n_features = X.shape
        y = y.copy().astype(np.int32)
        y[y == 0] = -1

        self.w0 = 0.0  # bias
        self.w = np.zeros(n_features)
        np.random.seed(1234)
        scale = 1 / np.sqrt(self.n_factors)
        self.v = np.random.normal(scale = scale, size = (n_features, self.n_factors))

        history = []
        for epoch in range(self.n_iter):
            y_pred = self._predict(X)
            z = y_pred * y
            loss = np.log(1.0 + np.exp(-z)).mean()
            loss_gradient = -y / ((np.exp(z) + 1.0) * n_samples)

            w_gradient = np.dot(X.T, loss_gradient)
            self.w0 -= self.learning_rate * loss_gradient.sum()  # * 1 is omitted
            self.w -= self.learning_rate * (w_gradient + 2 * self.reg_w * self.w)

            # there's probably a way to vectorize this ...
            for i, x in enumerate(X):
                term = x.dot(self.v)
                for j in range(n_features):
                    v_gradient = loss_gradient[i] * (x[j] * (term - self.v[j] * x[j]))
                    self.v[j] -= self.learning_rate * (v_gradient + 2 * self.reg_v * self.v[j])

            # for n, x in enumerate(X):
            #     v = np.empty((n_features, self.n_factors))
            #     for i in range(n_features):
            #         for f in range(self.n_factors):
            #             s = 0.0
            #             for j in range(n_features):
            #                 s += self.v[j, f] * x[j]

            #             v[i, f] = x[i] * s - self.v[j, f] * x[i] ** 2

            #     self.v -= self.learning_rate * (loss_gradient[n] * v + 2 * self.reg_v * self.v)

            # for i in range(n_samples):
            #     x = X[i]
            #     summed = self.v.dot(x.T)
            #     for factor in range(self.n_factors):
            #         for feature in range(n_features):
            #             term = summed[factor] - self.v[factor, feature] * x[feature]
            #             v_gradient = loss_gradient[i] * (x[feature] * term)
            #             term = (v_gradient + 2 * self.reg_v * self.v[factor, feature])
            #             self.v[factor, feature] -= self.learning_rate * term
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


class FMRegressor(BaseEstimator, RegressorMixin):
    """
    Factorization machines implementation using SGD
    (Stochastic Gradient Descent) optimizer.

    References
    ----------
    Factorization Machines http://www.csie.ntu.edu.tw/~b97053/paper/Rendle2010FM.pdf
    """

    def __init__(self, n_iter = 30, learning_rate = 0.01, n_factors = 10,
                 reg_w = 0.1, reg_v = 0.1, random_state = 1234):
        self.reg_w = reg_w
        self.reg_v = reg_v
        self.n_iter = n_iter
        self.n_factors = n_factors
        self.random_state = random_state
        self.learning_rate = learning_rate

    def fit(self, X, y):
        # check input matrix
        n_samples, n_features = X.shape

        self.w0 = 0.0  # bias
        self.w = np.zeros(n_features)
        np.random.seed(1234)
        scale = 1 / np.sqrt(self.n_factors)
        self.v = np.random.normal(scale = scale, size = (n_features, self.n_factors))

        history = []
        for epoch in range(self.n_iter):
            y_pred = self.predict(X)
            loss = np.mean(0.5 * (y_pred - y) ** 2)
            loss_gradient = (y_pred - y) / n_samples

            w_gradient = np.dot(X.T, loss_gradient)
            self.w0 -= self.learning_rate * loss_gradient.sum()  # * 1 is omitted
            self.w -= self.learning_rate * (w_gradient + 2 * self.reg_w * self.w)

            # there's probably a way to vectorize this ...
            # for i, x in enumerate(X):
            #     term = x.dot(self.v)
            #     for j in range(n_features):
            #         v_gradient = loss_gradient[i] * (x[j] * (term - self.v[j] * x[j]))
            #         self.v[j] -= self.learning_rate * (v_gradient + 2 * self.reg_v * self.v[j])

            # for n, x in enumerate(X):
            #     v = np.empty((n_features, self.n_factors))
            #     for i in range(n_features):
            #         for f in range(self.n_factors):
            #             s = 0.0
            #             for j in range(n_features):
            #                 s += self.v[j, f] * x[j]

            #             v[i, f] = x[i] * s - self.v[j, f] * x[i] ** 2

            #     self.v -= self.learning_rate * (loss_gradient[n] * v + 2 * self.reg_v * self.v)

            # for i in range(n_samples):
            #     x = X[i]
            #     summed = self.v.dot(x.T)
            #     for factor in range(self.n_factors):
            #         for feature in range(n_features):
            #             term = summed[factor] - self.v[factor, feature] * x[feature]
            #             v_gradient = loss_gradient[i] * (x[feature] * term)
            #             term = (v_gradient + 2 * self.reg_v * self.v[factor, feature])
            #             self.v[factor, feature] -= self.learning_rate * term
            history.append(loss)

        self.history = history
        return self

    def predict(self, X):
        linear_output = np.dot(X, self.w)
        term = np.dot(X, self.v) ** 2 - np.dot(X ** 2, self.v ** 2)
        factor_output = 0.5 * np.sum(term, axis = 1)
        return self.w0 + linear_output + factor_output
