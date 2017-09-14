import numpy as np
from collections import defaultdict
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler


class Preprocess(BaseEstimator, TransformerMixin):
    """
    Generic data preprocessing including:
    - standardize numeric columns
    - one-hot encode categorical columns

    Parameters
    ----------
    num_cols : list
        Numeric column's name.

    cat_cols : list
        Categorical column's name.

    Attributes
    ----------
    colnames_ : list
        Column name of the transformed numpy array.

    label_encode_dict_ : dict of sklearn's LabelEncoder
        LabelEncoder that was used to encode the value
        of the categorical columns into with value between
        0 and n_classes-1. Categorical columns will go through
        this encoding process before being one-hot encoded.

    cat_encode_ : sklearn's OneHotEncoder
        OneHotEncoder that was used to one-hot encode the
        categorical columns.

    scaler_ : sklearn's StandardScaler
        Scaler that was used to standardize the numeric columns.
    """

    def __init__(self, num_cols = None, cat_cols = None):
        self.num_cols = num_cols
        self.cat_cols = cat_cols

    def fit(self, data):
        """
        Fit the Preprocess

        Parameters
        ----------
        data : DataFrame
        """
        data = data.copy()

        # Label encoding across multiple columns in scikit-learn
        # https://stackoverflow.com/questions/24458645/label-encoding-across-multiple-columns-in-scikit-learn
        if self.cat_cols is not None:
            self.label_encode_dict_ = defaultdict(LabelEncoder)
            label_encoded = (data[self.cat_cols]
                             .apply(lambda x: self.label_encode_dict_[x.name].fit_transform(x)))

            self.cat_encode_ = OneHotEncoder(sparse = False)
            self.cat_encode_.fit(label_encoded)

        if self.num_cols is not None:
            self.scaler_ = StandardScaler().fit(data[self.num_cols])

        # store the column names (numeric columns comes before the
        # categorical columns) so we can refer to them later
        if self.num_cols is not None:
            colnames = self.num_cols.copy()
        else:
            colnames = []

        if self.cat_cols is not None:
            for col in self.cat_cols:
                cat_colnames = [col + '_' + str(classes)
                                for classes in self.label_encode_dict_[col].classes_]
                colnames += cat_colnames

        self.colnames_ = colnames
        return self

    def transform(self, data):
        """
        Trasform the data using the fitted Preprocess

        Parameters
        ----------
        data : DataFrame
        """
        if self.cat_cols is not None:
            label_encoded = (data[self.cat_cols]
                             .apply(lambda x: self.label_encode_dict_[x.name].transform(x)))
            cat_encoded = self.cat_encode_.transform(label_encoded)

        if self.num_cols is not None:
            scaled = self.scaler_.transform(data[self.num_cols])

        # combine encoded categorical columns and scaled numerical
        # columns, it's the same as concatenate it along axis 1
        if self.cat_cols is not None and self.num_cols is not None:
            X = np.hstack((scaled, cat_encoded))
        elif self.num_cols is None:
            X = cat_encoded
        else:
            X = scaled

        return X
