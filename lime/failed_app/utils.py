import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import randint
from collections import defaultdict
from bokeh.models import Span, HoverTool
from bokeh.layouts import gridplot, widgetbox
from bokeh.plotting import figure, ColumnDataSource
from bokeh.models.widgets import DataTable, TableColumn
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RandomizedSearchCV
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler


__all__ = [
    'clean',
    'viz_importance',
    'Preprocesser']

# sklearn's LinearRegression may give harmless errors
# https://github.com/scipy/scipy/issues/5998
warnings.filterwarnings(
    action = 'ignore', module = 'scipy', message = '^internal gelsd')


def clean(filepath, str_cols, cat_cols, num_cols, date_cols, ids_col, label_col = None):
    """
    Clean the raw dataset, targeted for this specific problem. Details
    of the preprocessing steps are commented within the function.

    Parameters
    ----------
    filepath : str
        Relative filepath of the data.

    str_cols : list[str]
        String features' column names. str_cols are essentially
        categorical columns (cat_cols), but includes NA values,
        thus they are read in as is and converted to categorical
        type after imputing the unknowns.

    cat_cols : list[str]
        Categorical features' column names.

    num_cols : list[str]
        Numeric features' column names.

    date_cols : list[str]
        Datetime features' column names.

    ids_col : str
        ID column name.

    label_col : str, default None
        Label column's name, None indicates that we're dealing with
        new data that does not have the label column.

    Returns
    -------
    data : DataFrame
        Cleaned data.
    """

    # information used when reading in the .csv file
    cat_dtypes = {col: 'category' for col in cat_cols}
    read_csv_info = {'dtype': cat_dtypes,
                     'parse_dates': date_cols,
                     'infer_datetime_format': True}
    use_cols = str_cols + cat_cols + num_cols + date_cols + [ids_col]
    if label_col is not None:
        use_cols += [label_col]

    # TODO:
    # letting pandas perform automatic date parsing seems to be slow
    data = pd.read_csv(filepath, usecols = use_cols, **read_csv_info)

    # NAN is filled with "N", after that we can
    # safely convert them to categorical type
    data[str_cols] = data[str_cols].fillna('N')
    for str_col in str_cols:
        data[str_col] = data[str_col].astype('category')

    # compute all time difference features:
    # source is measured in minutes
    delta = data['datetime_sourced'] - data['datetime_ordered']
    data['delta_source'] = data['deadline_source'] - (delta.dt.seconds / 60)

    # make is measured in hours
    delta = data['datetime_product_ready'] - data['datetime_sourced']
    data['delta_make'] = data['deadline_make'] - (delta.dt.seconds / 60 / 60)

    # deliver is measured in days
    delta = data['datetime_delivered'] - data['datetime_product_ready']
    data['delta_deliver'] = data['deadline_deliver'] - delta.dt.days

    # planning does not have a deadline
    data['delta_planned'] = (data['datetime_planned'] - data['datetime_ordered']).dt.days
    return data


def build_pipeline(num_cols, cat_cols, n_iter, cv, cache_dir):
    """
    Build a RandomSearchCV Pipeline RandomForest model

    Parameters
    ----------
    num_cols : list[str]
        Numeric columns' name.

    cat_cols : list[str]
        Categorical columns' name.

    n_iter : int
        Number of hyperparameters to try for RandomSearchCV

    cv : int
        Number of cross validation for RandomSearchCV

    cache_dir : str
        A temporary directory created by tempfile.mkdtemp

    Returns
    -------
    pipeline_tuned : sklearn's RandomSearchCV object
        Unfitted RandomSearchCV Pipeline model
    """
    preprocesser = Preprocesser(num_cols, cat_cols)
    rf = RandomForestClassifier(class_weight = 'balanced', n_jobs = -1)
    pipeline = Pipeline([
        ('preprocesser', preprocesser),
        ('rf', rf)
    ], memory = cache_dir)

    # set up randomsearch hyperparameters:
    # maximum tree depth and number of trees are presumably the most
    # common way to control under/overfitting for random forest models
    tuned_params = {
        'rf__max_depth': randint(low = 3, high = 12),
        'rf__n_estimators': randint(low = 50, high = 200)}

    # computing the scores on the training set can be computationally
    # expensive and is not strictly required to select the parameters
    # that yield the best generalization performance.
    pipeline_tuned = RandomizedSearchCV(
        estimator = pipeline,
        param_distributions = tuned_params,
        cv = cv,
        n_iter = n_iter,
        n_jobs = -1,
        verbose = 1,
        return_train_score = False)
    return pipeline_tuned


def viz_importance(model, feature_names, threshold = 0.05):
    """
    Visualize the relative importance of predictors.

    Parameters
    ----------
    model : sklearn's ensemble tree model
        A ensemble tree model that contains the attribute
        ``feature_importances_``.

    feature_names : str 1d array or list
        Description feature names that corresponds to the
        feature importance.

    threshold : float, default 0.05
        Features that have importance scores lower than this
        threshold will not be presented in the plot, this assumes
        the sum of the feature importance sum up to 1.
    """
    if not hasattr(model, 'feature_importances_'):
        msg = '{} does not have the feature_importances_ attribute'
        ValueError(msg.format(model.__class__.__name__))

    # apart from the mean feature importance, for scikit-learn we can access
    # each individual tree's feature importance and compute the standard deviation
    imp = model.feature_importances_
    has_std = False
    if hasattr(model, 'estimators_'):
        has_std = True
        tree_importances = np.asarray([tree.feature_importances_
                                       for tree in model.estimators_])
    mask = imp > threshold
    importances = imp[mask]
    names = feature_names[mask]
    if has_std:
        importances_std = np.std(tree_importances[:, mask], axis = 0)

    idx = np.argsort(importances)
    names = names[idx]
    scores = importances[idx]
    if has_std:
        scores_std = importances_std[idx]

    y_pos = np.arange(1, len(importances) + 1)
    fig, ax = plt.subplots()
    if has_std:
        plt.barh(y_pos, scores, align = 'center', xerr = scores_std)
    else:
        plt.barh(y_pos, scores, align = 'center')

    plt.yticks(y_pos, names)
    plt.xlabel('Importance')
    plt.title('Feature Importance Plot')


def bokeh_explain_plot(explainer, feature_names, ids, data,
                       input_id, estimator, y_pred, threshold = 0.05):
    """"""

    # convert id to the row number to retrieve
    # the observation in numpy array format
    input_row = np.where(ids == input_id)[0][0]
    data_row = data[input_row]

    # obtain probability for both the whole dataset and the current
    # target observation.
    # TODO:
    # the y_pred_row is hard coded to only work for binary class right now
    y_pred_row = round(y_pred[input_row, 1], 3)

    # configured to only show the top 6 features,
    # to prevent showing features that have little
    # impact and will only clutter the page
    explained = explainer.explain_instance(
        data_row = data_row,
        predict_fn = estimator.predict_proba,
        num_features = 6)
    explained_info = explained.as_list()

    # create all bokeh plots and combine them to a single grid plot
    p1 = feature_importance_plot(
        feature_names, estimator.feature_importances_, threshold)
    p2 = feature_value_table(feature_names, data_row)
    p3 = explain_plot(input_id, explained_info)
    p4 = prob_hist_plot(input_id, y_pred, y_pred_row)
    grid = gridplot([[p1, p2], [p3, p4]])
    return grid


def feature_value_table(feature_names, data_row):
    """
    Feature and value table for a given input id.

    References
    ----------
    Bokeh Interaction data table
    - https://bokeh.pydata.org/en/latest/docs/user_guide/examples/interaction_data_table.html
    """
    source = ColumnDataSource({
        'feature_names': feature_names,
        'value': data_row})

    columns = [
        TableColumn(field = 'feature_names', title = 'Feature'),
        TableColumn(field = 'value', title = 'Value')]

    data_table = DataTable(
        source = source, columns = columns, width = 500, height = 400)
    feature_table = widgetbox(data_table)
    return feature_table


def feature_importance_plot(feature_names, feature_importances, threshold):

    # select the top features that surpasses the defined threshold
    mask = feature_importances > threshold
    importances = feature_importances[mask]
    names = feature_names[mask]
    idx = np.argsort(importances)
    names = names[idx]
    importances = importances[idx]
    indices = np.arange(names.size)

    imp_col = 'importance'
    index_col = 'index'
    variable_col = 'variable'
    source = ColumnDataSource({
        index_col: indices,
        variable_col: names,
        imp_col: importances})
    p = figure(plot_width = 700, plot_height = 400, tools = '',
               title = 'Holistic Feature Importance')
    p.ygrid.grid_line_color = None
    p.xaxis.axis_label = imp_col
    p.yaxis.axis_label = variable_col

    # limit the position of the ticks, and specify the
    # label for each tick using the major_label_overrides attribute,
    # note that the key of the dictionary needs to be string type
    p.yaxis.ticker = indices
    p.yaxis.major_label_overrides = dict(zip(indices.astype(str), names))

    # hover tool will display the variable and its actual weight
    # field names that begin with @ are associated with columns in a ColumnDataSource
    tooltips = [
        (variable_col, '@' + variable_col),
        (imp_col, '@' + imp_col + '{0.2f}')]
    p.add_tools(HoverTool(tooltips = tooltips))
    p.hbar(y = index_col, right = imp_col, source = source,
           height = 0.5, line_color = 'white', hover_line_color = 'black')
    return p


def explain_plot(input_id, explained_info):

    # fix the column name up front
    index_col = 'index'
    variable_col = 'variable'
    weight_col = 'weight'
    color_col = 'color'

    def assign_color2weight(df):
        """
        positive weight corresponds to a light green color,
        whereas negative weight corresponds to a light red
        """
        df[color_col] = (df[weight_col].
                         apply(lambda w: '#99d594' if w > 0 else '#d53e4f'))
        return df

    # sort the weight in descending order so variables that have positive
    # or negative contributions will be grouped together in the resulting plot
    df = (pd.DataFrame(explained_info, columns = [variable_col, weight_col]).
          pipe(assign_color2weight).
          sort_values(weight_col))
    df[index_col] = np.arange(len(explained_info))

    # https://bokeh.pydata.org/en/latest/docs/user_guide/tools.html#hovertool
    source = ColumnDataSource(data = df.to_dict(orient = 'list'))
    p = figure(plot_width = 700, plot_height = 400, tools = '',
               title = 'Explanation for ID {}'.format(input_id))
    p.ygrid.grid_line_color = None
    p.xaxis.axis_label = weight_col
    p.yaxis.axis_label = variable_col

    # limit the position of the ticks, and specify the
    # label for each tick using the major_label_overrides attribute,
    # note that the key of the dictionary needs to be string type
    p.yaxis.ticker = df[index_col]
    p.yaxis.major_label_overrides = dict(zip(df[index_col].astype(str), df[variable_col]))

    # hover tool will display the variable and its actual weight
    # field names that begin with @ are associated with columns in a ColumnDataSource
    tooltips = [
        (variable_col, '@' + variable_col),
        (weight_col, '@' + weight_col + '{0.2f}')]
    p.add_tools(HoverTool(tooltips = tooltips))
    p.hbar(y = index_col, right = weight_col, color = color_col,
           hover_fill_color = color_col, source = source,
           height = 0.5, line_color = 'white', hover_line_color = 'black')
    return p


def prob_hist_plot(input_id, y_pred_data, y_pred_row):
    """
    Draw a histogram of the predicted probabilities.

    References
    ----------
    Bokeh Histogram
    - https://bokeh.pydata.org/en/latest/docs/gallery/histogram.html
    """
    title = 'Predicted Probability for ID {}: {}'.format(input_id, y_pred_row)
    p = figure(plot_width = 500, plot_height = 400, title = title, tools = '')

    # use .quad to draw rectangles, in this case our histograms
    # https://bokeh.pydata.org/en/latest/docs/user_guide/plotting.html#bars-and-rectangles
    # TODO:
    # need to investigate if calculating the histogram will become a bottleneck
    hist, edges = np.histogram(y_pred_data, density = True, bins = 50)
    p.quad(top = hist, bottom = 0, left = edges[:-1],
           right = edges[1:], line_color = 'white')

    # add vertical line indicating where the current observation's probability
    # sits compared to all other training data's predicted probabilities
    # http://bokeh.pydata.org/en/latest/docs/user_guide/annotations.html#spans
    vline = Span(
        location = y_pred_row, dimension = 'height',
        line_color = 'red', line_dash = 'dashed',
        line_width = 3)
    p.add_layout(vline)

    p.xaxis.axis_label = 'predicted probability'
    p.yaxis.axis_label = 'overall frequency'
    return p


def write_output(ids, ids_col, y_pred, label_col, output_path):
    """
    Output a DataFrame with the id columns and its predicted probability.

    Parameters
    ----------
    ids : 1d ndarray
        ID for each oberservation.

    ids_col : str
        ID column's name.

    y_pred : 1d ndarray
        Predicted probability for each oberservation.

    label_col : str
        Label column's name.

    output_path : str
        Relative path of the output file.
    """
    output = pd.DataFrame({
        ids_col: ids,
        label_col: y_pred
    }, columns = [ids_col, label_col])
    output.to_csv(output_path, index = False)


class Preprocesser(BaseEstimator, TransformerMixin):
    """
    Generic data preprocessing including:
    - standardize numeric columns and remove potential
    multi-collinearity using variance inflation factor
    - one-hot encode categorical columns

    Parameters
    ----------
    num_cols : list[str], default None
        Numeric columns' name. default None means
        the input column has no numeric features.

    cat_cols : list[str], default None
        Categorical columns' name.

    threshold : float, default 5.0
        Threshold for variance inflation factor (vif).
        If there are numerical columns, identify potential multi-collinearity
        between them using vif. Conventionally, a vif score larger than 5
        should be removed.

    Attributes
    ----------
    colnames_ : str 1d ndarray
        Column name of the transformed numpy array.

    num_cols_ : str 1d ndarray or None
        Final numeric column after removing potential multi-collinearity,
        if there're no numeric input features then the value will be None.

    label_encode_dict_ : defauldict of sklearn's LabelEncoder object
        LabelEncoder that was used to encode the value
        of the categorical columns into with value between
        0 and n_classes-1. Categorical columns will go through
        this encoding process before being one-hot encoded.

    cat_encode_ : sklearn's OneHotEncoder object
        OneHotEncoder that was used to one-hot encode the
        categorical columns.

    scaler_ : sklearn's StandardScaler object
        StandardScaler that was used to standardize the numeric columns.
    """

    def __init__(self, num_cols = None, cat_cols = None, threshold = 5.0):
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

        y : default None
            Ignore, argument required for constructing sklearn Pipeline

        Returns
        -------
        self
        """
        if self.num_cols is None and self.cat_cols is None:
            raise ValueError("There must be a least one input feature column")

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
            self.num_cols_ = np.array(colnames)
        else:
            colnames = []
            self.num_cols_ = None

        # store the column names (numeric columns comes before the
        # categorical columns) so we can refer to them later
        if self.cat_cols is not None:
            for col in self.cat_cols:
                cat_colnames = [col + '_' + str(classes)
                                for classes in self.label_encode_dict_[col].classes_]
                colnames += cat_colnames

        self.colnames_ = np.asarray(colnames)
        return self

    def _remove_collinearity(self, scaled):
        """
        Identify multi-collinearity between the numeric variables
        using variance inflation factor (vif)
        """
        colnames = self.num_cols.copy()
        while True:
            vif = [self._compute_vif(scaled, index)
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

    def _compute_vif(self, X, target_index):
        """
        Similar implementation as statsmodel's variance_inflation_factor
        with some enhancemants:
        1. includes the intercept by default
        2. prevents float division errors (dividing by 0)

        References
        ----------
        http://www.statsmodels.org/dev/generated/statsmodels.stats.outliers_influence.variance_inflation_factor.html
        """
        n_features = X.shape[1]
        X_target = X[:, target_index]
        mask = np.arange(n_features) != target_index
        X_not_target = X[:, mask]

        linear = LinearRegression()
        linear.fit(X_not_target, X_target)
        rsquared = linear.score(X_not_target, X_target)
        vif = 1. / (1. - rsquared + 1e-5)
        return vif

    def transform(self, data):
        """
        Transform the input data using Preprocess Transformer.

        Parameters
        ----------
        data : DataFrame, shape [n_samples, n_features]
            Input data

        Returns
        -------
        X : 2d ndarray, shape [n_samples, n_features]
            Transformed input data
        """
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
