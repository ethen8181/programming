import numpy as np


class SVM:
    """
    Multi-class Support Vector Machines (SVM) using gradient descent

    Parameters
    ----------
    learning_rate : float, default 1e-3
        Learning rate for optimization.

    reg : float, default 1e-5
        Regularization strength.

    n_iters : int, 100
        Number of iteration to run the optimization.

    Attributes
    ----------
    self.history_ : list
        Loss function at each iteration.

    self.weight_ : 2d ndarray, shape [n_features, n_classes]
        Weight for the svm model.
    """

    def __init__(self, learning_rate = 1e-3, reg = 1e-5, n_iters = 100):
        self.reg = reg
        self.n_iters = n_iters
        self.learning_rate = learning_rate

    def fit(self, X, y):
        """
        Fit the SVM model according to the given training data.

        Parameters
        ----------
        X : 2d ndarray, shape [n_samples, n_features]
            Training vectors, where n_samples is the number of samples
            and n_features is the number of features

        y : 1d ndarray, shape [n_samples]
            Target values (class labels in classification)
        """
        n_features = X.shape[1]
        n_classes = np.unique(y).shape[0]
        self.weight_ = np.random.randn(n_features, n_classes) * 0.01

        # run gradient descent to optimize W
        self.history_ = []
        for _ in range(self.n_iters):
            loss, gradient = self._loss(X, y)
            self.history_.append(loss)
            self.weight_ -= self.learning_rate * gradient

        return self

    def _loss(self, X, y):
        """Evaluate loss and gradient"""

        # scores shape: [sample, class]
        # every samples' score for every class
        n_samples = X.shape[0]
        scores = np.dot(X, self.weight_)

        # obtain the labeled class scores for each sample
        correct_scores = scores[range(n_samples), y]

        # sum up all the margin errors for the data loss
        # remember that we shouldn't count the j = y_i term (set it back to 0)
        margin = np.maximum(0, scores - correct_scores[:, np.newaxis] + 1)
        margin[range(n_samples), y] = 0

        loss_data = np.sum(margin) / n_samples
        loss_reg = 0.5 * self.reg * np.sum(self.weight_ ** 2)
        loss = loss_data + loss_reg

        # for j != y_i, it's a indicator function of
        # whether its margin is greater than 1
        gradient = np.zeros(scores.shape)
        gradient[margin > 0] = 1

        # for j = y_i
        # number of times that the margin is greater than 0
        count = np.sum(gradient, axis = 1)
        gradient[range(n_samples), y] = -count

        gradient_data = np.dot(X.T, gradient) / n_samples
        gradient_reg = self.reg * self.weight_
        gradient = gradient_data + gradient_reg
        return loss, gradient

    def predict(self, X):
        """
        Prediction of class labels on the input data using the trained model

        Parameters
        ----------
        X : 2d ndarray, shape [n_samples, n_features]
            Input data, where n_samples is the number of samples
            and n_features is the number of features

        Returns
        -------
        y_pred : 1d ndarray, shape [n_samples]
            Predicted labels for the input data
        """
        score = np.dot(X, self.weight_)
        y_pred = np.argmax(score, axis = 1)
        return y_pred
