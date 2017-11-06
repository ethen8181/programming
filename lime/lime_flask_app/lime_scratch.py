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

    def __init__(self, feature_names, categorical_features,
                 discretize = 'quartile', random_state = 1234):
        self.discretize = discretize
        self.random_state = random_state
        self.feature_names = feature_names  # ?? change to "colnames"
        self.categorical_features = categorical_features  # ?? string and change to 'cat_cols'

    def fit(self, data):

        # discretize numeric features
        categorical_features = self.categorical_features
        if self.discretize is not None:
            self._discretize_numeric(data)

            # ?? can this be returned by discretized numeric
            discretized_data = self._discretize(data)
            categorical_features = range(data.shape[1])

        # ?? again, is this separate dictionary required
        feature_values = {}
        feature_frequencies = {}
        for feature in categorical_features:
            if self.discretize is None:
                column = data[:, feature]
            else:
                column = discretized_data[:, feature]

            values, freq = np.unique(column, return_counts = True)
            freq /= freq.sum()
            feature_values[feature] = values
            feature_frequencies[feature] = freq

        self.feature_values_ = feature_values
        self.feature_frequencies_ = feature_frequencies

        return self

    def explain_instance(self, data_row, n_samples = 10):
        """
        Generates explanations for a prediction.

        First, we generate neighborhood data by randomly perturbing features
        from the instance. We then learn locally weighted linear models on this
        neighborhood data to explain each of the classes in an interpretable way
        """

        return self

    def _data_inverse(self, data_row, n_samples):

        return self

    def _discretize_numeric(self, data):
        self.to_discretize_ = [x for x in range(data.shape[1])
                               if x not in self.categorical_features]

        # 1. whether to bin them all into a dictionary of namedtuples ??
        # currently the key is the integer index of each numeric feature
        # 2. init as local variable and assign to class attribute at the end
        self.bins_ = {}
        self.names_ = {}
        self.means = {}
        self.stds = {}
        self.mins = {}
        self.maxs = {}
        for feature in self.to_discretize_:
            if self.discretize == 'quartile':
                unique_bins = self._get_bins(data[:, feature])

            self.bins_[feature] = unique_bins

            # create the binned feature name
            n_bins = unique_bins.size
            name = self.feature_names[feature]
            binned_names = ['{} <= {:.2f}'.format(name, unique_bins[0])]
            for i in range(1, n_bins - 1):
                binned_name = '{:.2f} < {} <= {:.2f}'.format(
                    unique_bins[i], name, unique_bins[i + 1])
                binned_names.append(binned_name)

            binned_names.append('{} > {:.2f}'.format(name, unique_bins[n_bins - 1]))
            self.names_[feature] = binned_names

            data_feature = data[:, feature]
            discretized = self._discretize(data_feature, unique_bins)

            # mean and std for each bin
            # (add the small constant to prevent division error)
            self.means[feature] = []
            self.stds[feature] = []
            for binned in range(1, n_bins):
                binned_feature = data_feature[discretized == binned]
                mean = 0 if len(binned_feature) == 0 else np.mean(binned_feature)
                std = 0 if len(binned_feature) == 0 else np.std(binned_feature)
                std += 0.00000000001
                self.means[feature].append(mean)
                self.stds[feature].append(std)

            # ?? not sure what this is doing
            self.mins[feature] = unique_bins[:n_bins - 1]
            self.maxs[feature] = unique_bins[1:]

    def _get_bins(self, x):
        """Returns the discretize boundary for the input feature"""

        # TODO :
        # quartile, implement other binning
        # TODO :
        # do we need to isolate the min and max from the percentile
        # calculation to ensure it won't get dropped when calling unique
        percentiles = np.percentile(x, [0, 25, 50, 75, 100])
        unique_bins = np.unique(percentiles)
        return unique_bins

    def _discretize(self, data, unique_bins = None):
        """Discretize the input data, if feature is not specified then discretize all"""
        X = data.copy()
        if unique_bins is None:
            for feature, unique_bins in self.bins_.items():
                X[:, feature] = np.searchsorted(unique_bins, X[:, feature])
        else:
            X = np.searchsorted(unique_bins, X)

        return X

    # def _undiscretize(self, data):
    #     ret = data.copy()
    #     for feature in self.means:
    #         mins = self.mins[feature]
    #         maxs = self.maxs[feature]
    #         means = self.means[feature]
    #         stds = self.stds[feature]

    #         rstate = np.random.RandomState(self.random_state)

    #         def get_inverse(q):
    #             return max(mins[q],
    #                        min(rstate.normal(means[q], stds[q]), maxs[q]))
    #         if len(data.shape) == 1:
    #             q = int(ret[feature])
    #             ret[feature] = get_inverse(q)
    #         else:
    #             ret[:, feature] = (
    #                 [get_inverse(int(x)) for x in ret[:, feature]])
    #     return ret
