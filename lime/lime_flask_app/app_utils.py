import os
import bokeh
import requests
import numpy as np
import pandas as pd
from joblib import load
from bokeh.embed import components
from bokeh.models import HoverTool
from bokeh.plotting import figure, ColumnDataSource
from lime.lime_tabular import LimeTabularExplainer

__all__ = [
    'bokeh_css_javascript',
    'explain_plot']

model = load('model.pkl')

# explainer not pickable
X = np.load('data.npz')['data']
explainer = LimeTabularExplainer(
    X,
    feature_names = ['sepal length (cm)', 'sepal width (cm)',
                     'petal length (cm)', 'petal width (cm)'],
    class_names = ['setosa', 'versicolor', 'virginica'],
    discretize_continuous = True)


def bokeh_css_javascript():
    """
    To add custom CSS or Javascript (in this case Bokeh) to
    Flask Bootstrap we need to save them to a folder called "static"

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


def explain_plot(input_id):
    explained = explainer.explain_instance(
        X[input_id], model.predict_proba,
        num_features = X.shape[1], top_labels = 0)
    explained_info = explained.as_list()

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

    # Generate the script and HTML for the plot
    plot_script, plot_div = components(p)
    return plot_script, plot_div
