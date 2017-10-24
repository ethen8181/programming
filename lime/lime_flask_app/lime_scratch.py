import numpy as np
# from abc import ABCMeta, abstractmethod


# class LimeTabluarExplainer:

#     def __init__(self, feature_names, random_state,
#                  discretize, discretizer = 'quartile'):
#         self.feature_names = feature_names
#         self.random_state = random_state
#         self.discretize = discretize
#         self.discretizer = discretizer

#     def fit(self, data):
#         if self.discretize:
#             if self.discretizer == 'quartile':
#                 1 + 1
#                 # discretizer = QuartileDiscretizer(X, )

#         return self


class Discretizer:

    # __metaclass__ = ABCMeta

    def __init__(self, feature_names, categorical_features):
        self.feature_names = feature_names
        self.categorical_features = categorical_features  # ??

    def fit(self, data):
        self.to_discretize_ = [x for x in range(data.shape[1])
                               if x not in self.categorical_features]
        self.bins_ = {}
        self.names_ = {}
        for feature in self.to_discretize_:
            unique_bins = self._get_bins(data[:, feature])
            self.bins_[feature] = unique_bins

            # create the binned feature name
            n_bins = len(unique_bins)
            name = self.feature_names[feature]
            binned_features = ['{} <= {:.2f}'.format(name, unique_bins[0])]
            for i in range(1, n_bins - 1):
                binned_feature = '{:.2f} < {} <= {:.2f}'.format(
                    unique_bins[i], name, unique_bins[i + 1])
                binned_features.append(binned_feature)

            binned_features.append('{} > {:.2f}'.format(name, unique_bins[n_bins - 1]))
            self.names_[feature] = binned_features

        return self

    def _get_bins(self, x):
        # TODO :
        # quartile, implement other binning
        percentiles = np.percentile(x, [0, 25, 50, 75, 100])
        unique_bins = np.unique(percentiles)
        return unique_bins

    def discretize(self, data):
        X = data.copy()
        for feature, unique_bins in self.bins_.items():
            X[:, feature] = np.searchsorted(unique_bins, X[:, feature])

        return X
