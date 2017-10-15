import numpy as np
import pandas as pd
import numpy.ma as ma
from collections import defaultdict
from scipy.stats import mode, boxcox
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler
from statsmodels.stats.outliers_influence import variance_inflation_factor


__all__ = ['MultipleImputer', 'BoxCoxTransformer', 'Preprocess']


class MultipleImputer(BaseEstimator, TransformerMixin):
    """
    Extends the sklearn Imputer Transformer [1]_ by allowing users
    to specify different imputing strategies for different columns

    Parameters
    ----------
    missing_values : float or "NaN"/np.nan, default "NaN"
        The placeholder for the missing values. All occurrences of
        `missing_values` will be imputed. For missing values encoded as np.nan,
        we can either use the string value "NaN" or np.nan.

    copy : bool, default True
        Set to False to perform inplace transformation.

    Attributes
    ----------
    statistics_ : 1d ndarray [n_features]
        The imputation fill value for each feature

    References
    ----------
    .. [1] `Scikit-learn Imputer
            <http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.Imputer.html>`_
    """

    def __init__(self, strategies, missing_values = "NaN", copy = True):
        self.copy = copy
        self.strategies = strategies
        self.missing_values = missing_values

    def fit(self, X, y = None):
        """
        Fit MultipleImputer to X.

        Parameters
        ----------
        X : 2d ndarray, shape [n_samples, n_features]
            Input data

        Returns
        -------
        self
        """
        allowed_strategies = {'mean', 'median', 'mode'}
        for k in self.strategies:
            if k not in allowed_strategies:
                msg = 'Can only use these strategies: {0} got strategy={1}'
                raise ValueError(msg.format(allowed_strategies, k))

        # introduction to masked array for those that are not familiar
        # https://docs.scipy.org/doc/numpy-1.13.0/reference/maskedarray.generic.html
        mask = self._get_mask(X, self.missing_values)
        X_masked = ma.masked_array(X, mask = mask)

        if 'mean' in self.strategies:
            mean_cols = self.strategies['mean']
            mean_masked = ma.mean(X_masked[:, mean_cols].astype(np.float64), axis = 0)

        if 'median' in self.strategies:
            median_cols = self.strategies['median']
            median_masked = ma.median(X_masked[:, median_cols].astype(np.float64), axis = 0)

        # numpy MaskedArray doesn't seem to support the .mode
        # method yet, thus we roll out our own
        # https://docs.scipy.org/doc/numpy-1.13.0/reference/maskedarray.baseclass.html#maskedarray-baseclass
        if 'mode' in self.strategies:
            mode_cols = self.strategies['mode']
            mode_values = np.empty(len(mode_cols))

            # transpose to compute along each column instead of row
            zipped = zip(X[:, mode_cols].T, mask[:, mode_cols].T)
            for i, (col, col_mask) in enumerate(zipped):
                col_valid = col[~col_mask]
                values, _ = mode(col_valid)
                mode_values[i] = values[0]

        statistics = ma.masked_all(X.shape[1])
        if 'mean' in self.strategies:
            statistics[mean_cols] = mean_masked.data

        if 'median' in self.strategies:
            statistics[median_cols] = median_masked.data

        if 'mode' in self.strategies:
            statistics[mode_cols] = mode_values

        self.statistics_ = statistics
        return self

    def _get_mask(self, X, value_to_mask):
        """Compute the boolean mask X == missing_values."""
        if value_to_mask == 'NaN' or np.isnan(value_to_mask):
            # TODO :
            # np.isnan or pd.isnull (this also works with object
            # type, but is it worth it?)
            return pd.isnull(X)
        else:
            return X == value_to_mask

    def transform(self, X):
        """
        Transform X using MultipleImputer.

        Parameters
        ----------
        X : 2d ndarray, shape [n_samples, n_features]
            Input data

        Returns
        -------
        X_transformed : 2d ndarray, shape [n_samples, n_features]
            Transformed input data
        """
        if self.copy:
            X = X.copy()

        mask = self._get_mask(X, self.missing_values)
        for strategy_cols in self.strategies.values():
            fill_value = self.statistics_[strategy_cols]
            for i, strategy_col in enumerate(strategy_cols):
                X[:, strategy_col][mask[:, strategy_col]] = fill_value[i]

        return X


class BoxCoxTransformer(BaseEstimator, TransformerMixin):
    """
    BoxCox transformation on individual features. It wil be applied on
    each feature (each column of the data matrix) with lambda evaluated
    to maximise the log-likelihood

    Parameters
    ----------
    transformed_features : int/bool 1d ndarray or "all"
        Specify what features are to be transformed.
        - "all" (default) : All features are to be transformed.
        - array of int : Array of feature indices to be transformed.
        - array of bool : Array of length n_features and with dtype=bool.

    copy : bool, default True
        Set to False to perform inplace transformation.

    Attributes
    ----------
    transformed_features_ : int 1d ndarray
        The indices of the features to be transformed

    lambdas_ : float 1d ndarray [n_transformed_features]
        The parameters of the BoxCox transform for the selected features.

    n_features_ : int
        Number of features inputted during fit

    Notes
    -----
    The Box-Cox transform is given by::
        y = (x ** lambda - 1.) / lmbda,  for lambda > 0
            log(x),                      for lambda = 0

    ``boxcox`` requires the input data to be positive.
    """

    def __init__(self, transformed_features, eps = 1e-8, copy = True):
        self.eps = eps
        self.copy = copy
        self.transformed_features = transformed_features

    def fit(self, X, y = None):
        """
        Fit BoxCoxTransformer to X.

        Parameters
        ----------
        X : 2d ndarray, shape [n_samples, n_feature]
            Input data

        Returns
        -------
        self
        """
        self.n_features_ = X.shape[1]
        if self.transformed_features == 'all':
            transformed_features = np.arange(self.n_features_)
        else:
            # use np.copy instead of the .copy method
            # ensures it won't break if the user inputted
            # transformed_features as a list
            transformed_features = np.copy(self.transformed_features)
            if transformed_features.dtype == np.bool:
                transformed_features = np.where(transformed_features)[0]

        if np.any(X[:, transformed_features] + self.eps <= 0):
            raise ValueError('BoxCox transform can only be applied on positive data')

        # TODO :
        # an embarrassingly parallelized problem, i.e.
        # each features' boxcox lambda can be estimated in parallel
        # needs to investigate if it's a bottleneck
        self.lmbdas_ = [self._boxcox(X[:, i]) for i in transformed_features]
        self.transformed_features_ = transformed_features
        return self

    def _boxcox(self, x, lmbda = None):
        """Utilize scipy's boxcox transformation"""
        x = x.astype(np.float64)
        mask = np.isnan(x)
        x_valid = x[~mask] + self.eps
        if lmbda is None:
            _, lmbda = boxcox(x_valid, lmbda)
            return lmbda
        else:
            x[~mask] = boxcox(x_valid, lmbda)
            return x

    def transform(self, X):
        """
        Transform X using BoxCoxTransformer.

        Parameters
        ----------
        X : 2d ndarray, shape [n_samples, n_features]
            Input data

        Returns
        -------
        X_transformed : 2d ndarray, shape [n_samples, n_features]
            Transformed input data
        """
        if np.any(X[:, self.transformed_features_] + self.eps <= 0):
            raise ValueError('BoxCox transform can only be applied on positive data')

        if self.copy:
            X = X.copy()

        for i, feature in enumerate(self.transformed_features_):
            X[:, feature] = self._boxcox(X[:, feature], self.lmbdas_[i])

        return X


class Preprocess(BaseEstimator, TransformerMixin):
    """
    Generic data preprocessing including:
    - standardize numeric columns and remove potential
    multi-collinearity using variance inflation factor
    - one-hot encode categorical columns

    Parameters
    ----------
    num_cols : list[str], default None
        Numeric columns' name. default None means
        the input column has no numeric features

    cat_cols : list[str], default None
        Categorical columns' name

    threshold : int, default 5
        Threshold for variance inflation factor (vif).
        If there are numerical columns, identify potential multi-collinearity
        between them using (vif). Conventionally, a vif score larger than 5
        should be removed

    Attributes
    ----------
    colnames_ : list[str]
        Column name of the transformed numpy array

    num_cols_ : list[str] or None
        Final numeric column after removing potential multi-collinearity,
        if there're no numeric input features then the value will be None

    label_encode_dict_ : defauldict of sklearn's LabelEncoder object
        LabelEncoder that was used to encode the value
        of the categorical columns into with value between
        0 and n_classes-1. Categorical columns will go through
        this encoding process before being one-hot encoded

    cat_encode_ : sklearn's OneHotEncoder object
        OneHotEncoder that was used to one-hot encode the
        categorical columns

    scaler_ : sklearn's StandardScaler object
        StandardScaler that was used to standardize the numeric columns
    """

    def __init__(self, num_cols = None, cat_cols = None, threshold = 5):
        self.num_cols = num_cols
        self.cat_cols = cat_cols
        self.threshold = threshold

    def fit(self, data, y = None):
        """
        Fit the Preprocess Transformer on the input data.

        Parameters
        ----------
        data : DataFrame, shape [n_samples, n_features]
            Input data

        Returns
        -------
        self
        """
        if self.num_cols is None and self.cat_cols is None:
            raise ValueError("There must be a least one input feature column")

        # TODO : fix this for both DataFrame and numpy or restrict to one of them
        data = pd.DataFrame(data.copy())

        # Label encoding across multiple columns in scikit-learn
        # https://stackoverflow.com/questions/24458645/label-encoding-across-multiple-columns-in-scikit-learn
        if self.cat_cols is not None:
            self.label_encode_dict_ = defaultdict(LabelEncoder)
            label_encoded = (data[self.cat_cols].
                             apply(lambda x: self.label_encode_dict_[x.name].fit_transform(x)))

            self.cat_encode_ = OneHotEncoder(sparse = False)
            self.cat_encode_.fit(label_encoded)

        if self.num_cols is not None:
            self.scaler_ = StandardScaler()
            scaled = self.scaler_.fit_transform(data[self.num_cols])
            colnames = self._remove_collinearity(scaled)
            self.num_cols_ = colnames.copy()
        else:
            colnames = []
            self.num_cols_ = None

        # store the column names (numeric columns comes before the
        # categorical columns) so we can refer to them later
        if self.cat_cols is not None:
            for col in self.cat_cols:
                # TODO : is str(col) neccessary or just col
                cat_colnames = [str(col) + '_' + str(classes)
                                for classes in self.label_encode_dict_[col].classes_]
                colnames += cat_colnames

        self.colnames_ = colnames
        return self

    def _remove_collinearity(self, scaled):
        """
        Identify multi-collinearity between the numeric variables
        using variance inflation factor (vif)
        """
        colnames = self.num_cols.copy()
        while True:
            vif = [variance_inflation_factor(scaled, index)
                   for index in range(scaled.shape[1])]
            max_index = np.argmax(vif)

            if vif[max_index] >= self.threshold:
                removed = colnames[max_index]
                colnames.remove(removed)
                scaled = np.delete(scaled, max_index, axis = 1)
                self.scaler_.mean_ = np.delete(self.scaler_.mean_, max_index)
                self.scaler_.scale_ = np.delete(self.scaler_.scale_, max_index)
            else:
                break

        return colnames

    def transform(self, data):
        """
        Transform X using Preprocess Transformer.

        Parameters
        ----------
        X : DataFrame, shape [n_samples, n_features]
            Input data

        Returns
        -------
        X_transformed : 2d ndarray, shape [n_samples, n_features]
            Transformed input data
        """
        data = pd.DataFrame(data.copy())
        if self.cat_cols is not None:
            label_encoded = (data[self.cat_cols].
                             apply(lambda x: self.label_encode_dict_[x.name].transform(x)))
            cat_encoded = self.cat_encode_.transform(label_encoded)

        if self.num_cols is not None:
            scaled = self.scaler_.transform(data[self.num_cols_])

        # combine encoded categorical columns and scaled numerical
        # columns, it's the same as concatenate it along axis 1
        if self.cat_cols is not None and self.num_cols is not None:
            X = np.hstack((scaled, cat_encoded))
        elif self.num_cols is None:
            X = cat_encoded
        else:
            X = scaled

        return X
