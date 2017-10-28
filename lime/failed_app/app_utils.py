import os
import bokeh
import requests
import numpy as np
import pandas as pd
from joblib import load
from bokeh.embed import components
from bokeh.models import Span, HoverTool
from bokeh.layouts import gridplot, widgetbox
from bokeh.plotting import figure, ColumnDataSource
from bokeh.models.widgets import DataTable, TableColumn
from lime.lime_tabular import LimeTabularExplainer


__all__ = [
    'bokeh_css_javascript',
    'bokeh_explain_plot']


# a temporary bad hack to get around the fact that
# LimeTabularExplainer is not pickable

# model checkpoint:
MODEL_DIR = os.path.join('..', 'model')
LIME_CHECKPOINT = os.path.join(MODEL_DIR, 'lime.npz')
MODEL_CHECKPOINT = os.path.join(MODEL_DIR, 'pipeline.pkl')
ENCODER_CHECKPOINT = os.path.join(MODEL_DIR, 'encoder.pkl')

lime_info = np.load(LIME_CHECKPOINT)
pipeline = load(MODEL_CHECKPOINT)
label_encoder = load(ENCODER_CHECKPOINT)

# global information that will be used with plotting
best = pipeline.best_estimator_
estimator = best.named_steps['rf']
preprocessor = best.named_steps['preprocesser']

ids = lime_info['ids']
data = lime_info['X_data']
y_pred = lime_info['y_pred']
feature_names = preprocessor.colnames_

explainer = LimeTabularExplainer(
    training_data = data,
    feature_names = feature_names,
    class_names = label_encoder.classes_,
    discretize_continuous = True)


def bokeh_css_javascript():
    """
    To add custom CSS or Javascript (in this case Bokeh) to
    Flask Bootstrap we need to save them to a folder called "static"
    and add them to the template.

    Returns
    -------
    css_files : list[str]
        List of bokeh CSS files.

    js_files : list[str]
        List of bokeh Javascript files.

    References
    ----------
    Flask-Bootstrap Documentation
    - https://pythonhosted.org/Flask-Bootstrap/basic-usage.html#examples

    Bringing visualisation to the web with Python and Bokeh
    - https://summerofhpc.prace-ri.eu/bringing-visualisation-to-the-web-with-python-and-bokeh/
    """

    # bokeh's CSS and Javascript file is located at
    # from bokeh.resources import CDN
    # CDN.render_css() and CDN.render_js()
    # after viewing the link, we extract the file and save them if
    # it's not there already
    css_files = ['bokeh-' + name + bokeh.__version__ + '.min.css'
                 for name in ['', 'widgets-', 'tables-']]
    js_files = ['bokeh-' + name + bokeh.__version__ + '.min.js'
                for name in ['', 'widgets-', 'tables-', 'gl-']]

    folder = 'static'
    if not os.path.isdir(folder):
        os.mkdir(folder)
        base_path = 'https://cdn.pydata.org/bokeh/release/'
        for file in css_files + js_files:
            file_path = os.path.join(folder, file)
            with open(file_path, 'w') as f:
                content = requests.get(base_path + file).text
                f.write(content)

    return css_files, js_files


def bokeh_explain_plot(input_id, threshold = 0.05):
    """"""

    # convert id to the row number to retrieve
    # the observation in numpy array format
    input_row = np.where(ids == input_id)[0][0]
    data_row = data[input_row]

    # obtain probability for both the whole dataset and the current
    # target observation.
    # TODO:
    # the y_pred_row is hard coded to only work for binary class right now
    y_pred_data = estimator.predict_proba(data)
    y_pred_row = round(y_pred_data[input_row, 1], 3)

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
    p4 = prob_hist_plot(input_id, y_pred_data, y_pred_row)
    plot = gridplot([[p1, p2], [p3, p4]])

    # Generate the script and HTML for the plot
    plot_script, plot_div = components(plot)
    return plot_script, plot_div


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
