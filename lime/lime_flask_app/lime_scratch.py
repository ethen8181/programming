import numpy as np
from sklearn.metrics import pairwise_distances
from sklearn.preprocessing import StandardScaler


class Discretizer:

    def __init__(self, categorical_features, feature_names, class_names = None,
                 mode = 'classification', discretize = 'quartile', random_state = 1234):
        self.mode = mode
        self.class_names = class_names
        self.discretize = discretize
        self.random_state = random_state
        self.feature_names = feature_names  # ?? change to "colnames"
        self.categorical_features = categorical_features  # ?? string and change to 'cat_cols'

    def fit(self, data):

        categorical_features = self.categorical_features
        # discretize numerical features
        if self.discretize is not None:
            self._discretize_numeric(data)

            # ?? can this be returned by discretized numeric
            discretized_data = self._discretize(data)

            # after dicretizing numerical features, all columns
            # are considered categorical
            categorical_features = range(data.shape[1])

        # categorical feature's mean and std will be set of 0 and 1 later ...
        self.scaler = StandardScaler()
        self.scaler.fit(data)

        # ?? again, is this separate dictionary required
        # feature_frequency : proportion of each categories
        feature_values = {}
        feature_frequencies = {}
        for feature in categorical_features:
            if self.discretize is None:
                column = data[:, feature]
            else:
                column = discretized_data[:, feature]

            values, freq = np.unique(column, return_counts = True)
            # freq /= freq.sum() would result in type casting error
            freq = freq / freq.sum()
            feature_values[feature] = values
            feature_frequencies[feature] = freq

            self.scaler.mean_[feature] = 0
            self.scaler.scale_[feature] = 1

        self.feature_values_ = feature_values
        self.feature_frequencies_ = feature_frequencies
        self.categorical_features_ = categorical_features
        return self

    def explain_instance(self, data_row, predict_fn,
                         n_samples = 10, distance_metric = 'cosine'):
        """
        Generates explanations for a prediction.

        First, we generate neighborhood data by randomly perturbing features
        from the instance. We then learn locally weighted linear models on this
        neighborhood data to explain each of the classes in an interpretable way
        """
        data, inverse = self._data_inverse(data_row, n_samples)
        scaled_data = (data - self.scaler.mean_) / self.scaler.scale_
        distances = pairwise_distances(
            X = scaled_data,
            Y = scaled_data[0].reshape(1, -1),
            metric = distance_metric
        ).ravel()
        y_pred = predict_fn(inverse)

        if self.mode == 'classification':
            if len(y_pred.shape) == 2:
                if self.class_names is None:
                    self.class_names_ = [str(x) for x in range(y_pred.shape[1])]
                else:
                    self.class_names_ = list(self.class_names)
            else:
                raise ValueError(
                    'For classification, the model should output '
                    'a 2d array that contains the predicted probabability'
                    'got arrays with {} dimensions'.format(len(y_pred.shape)))
        else:  # assume regression
            if len(y_pred.shape) != 1:
                raise ValueError(
                    'For regression, the model should output single-dimensional '
                    'array, not arrays of {} dimensions'.format(len(y_pred.shape)))

        print(self.feature_names)

        return self

    def _data_inverse(self, data_row, n_samples):
        """
        For numerical features, perturb them by sampling from a Normal(0, 1) and
        perform a inverse operation of mean-centering and scaling, according to
        the means and stds in the training data. For categorical features,
        perturb by sampling according to the training distribution, and making
        a binary feature that is 1 when the value is the same as the instance
        being explained.

        Returns
        -------
        data : 2d ndarray
            Categorical features are encoded with either 0 (not equal to the
            corresponding value in data_row) or 1. The first row is  set to be
            the original instance.

        inverse : 2d ndarray
            Same as data, except the categorical features are not
            binary, but categorical (as the original data)
        """

        # this should probably be moved
        rstate = np.random.RandomState(self.random_state)

        n_features = data_row.size
        data = np.zeros((n_samples, n_features))
        categorical_features = range(n_features)
        if self.discretize is None:
            # there are both numerical and categorical features
            data = rstate.normal(0, 1, size = (n_samples, n_features))
            data = data * self.scaler.scale_ + self.scaler.mean_
            categorical_features = self.categorical_features_
            first_row = data_row
        else:
            first_row = self._discretize(data_row)

        # include the current data_row in the perturbation
        data[0] = data_row
        inverse = data.copy()
        for col in categorical_features:
            values = self.feature_values_[col]
            freqs = self.feature_frequencies_[col]
            inverse_col = rstate.choice(
                values, size = n_samples, replace = True, p = freqs)
            binary_col = (first_row[col] == inverse_col).astype(np.uint8)

            # include the current data_row in the perturbation
            binary_col[0] = 1
            inverse_col[0] = data[0, col]
            data[:, col] = binary_col
            inverse[:, col] = inverse_col

        if self.discretize is not None:
            inverse[1:] = self._undiscretize(inverse[1:])

        inverse[0] = data_row
        return data, inverse

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

            # where should the indentation be ??
            self.bins_[feature] = unique_bins

            # create the binned feature name
            n_bins = unique_bins.size
            name = self.feature_names[feature]
            binned_names = ['{} <= {:.2f}'.format(name, unique_bins[1])]
            for i in range(1, n_bins - 2):
                binned_name = '{:.2f} < {} <= {:.2f}'.format(
                    unique_bins[i], name, unique_bins[i + 1])
                binned_names.append(binned_name)

            binned_names.append('{} > {:.2f}'.format(name, unique_bins[n_bins - 2]))
            self.names_[feature] = binned_names

            data_feature = data[:, feature]
            discretized = self._discretize(data_feature, unique_bins)

            # mean and std for each bin
            # (add the small constant to prevent division error);
            # exclude the min and max boundary of the unique_bins
            feature_means = []
            feature_stds = []
            for binned in range(n_bins - 1):
                binned_feature = data_feature[discretized == binned]
                mean = 0 if len(binned_feature) == 0 else np.mean(binned_feature)
                std = 1e-6 if len(binned_feature) == 0 else np.std(binned_feature)
                feature_means.append(mean)
                feature_stds.append(std)

            self.means[feature] = np.asarray(feature_means)
            self.stds[feature] = np.asarray(feature_stds)

            # ?? not sure what this is doing,
            # we can most likely get it from the bins
            self.mins[feature] = unique_bins[:n_bins - 1]
            self.maxs[feature] = unique_bins[1:]

    def _get_bins(self, x):
        """Returns the discretize boundary for the input feature"""

        # TODO :
        # quartile, implement other binning

        # isolate the min and max from the percentile
        # calculation to ensure it won't get dropped when calling unique
        percentiles = np.percentile(x, [25, 50, 75])
        unique_bins = np.unique(percentiles)
        unique_bins = np.hstack((np.min(x), unique_bins, np.max(x)))
        return unique_bins

    def _discretize(self, data, unique_bins = None):
        """Discretize the input data, if feature is not specified then discretize all"""
        X = data.copy()
        if unique_bins is None:
            for feature, unique_bins in self.bins_.items():
                n_bins = unique_bins.size
                unique_bins = unique_bins[1:n_bins - 1]
                if len(data.shape) == 1:
                    X[feature] = np.searchsorted(unique_bins, X[feature])
                else:  # assumes 2d otherwise
                    X[:, feature] = np.searchsorted(unique_bins, X[:, feature])
        else:
            n_bins = unique_bins.size
            unique_bins = unique_bins[1:n_bins - 1]
            X = np.searchsorted(unique_bins, X)

        return X

    def _undiscretize(self, data):
        """"""
        X = data.copy()
        # this should probably be moved
        rstate = np.random.RandomState(self.random_state)
        for feature in self.means:
            mins = self.mins[feature]
            maxs = self.maxs[feature]
            means = self.means[feature]
            stds = self.stds[feature]

            binned = X[:, feature].astype(np.int)
            randn = rstate.normal(means[binned], stds[binned])
            X[:, feature] = np.maximum(mins[binned], np.minimum(maxs[binned], randn))

        return X
