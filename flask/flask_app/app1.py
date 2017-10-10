from flask import Flask
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import components
from bokeh.models import HoverTool
from bokeh.sampledata.glucose import data
app = Flask(__name__)


@app.route("/")
def visualisation():
    """
    References
    ----------
    Bringing visualisation to the web with Python and Bokeh
    - https://summerofhpc.prace-ri.eu/bringing-visualisation-to-the-web-with-python-and-bokeh/
    """

    # p = figure(plot_width=400, plot_height=400)
    # p.hbar(y=[1, 2, 3], height=0.5, left=0,
    #        right=[1.2, 2.5, 3.7], color="firebrick")

    subset = data.ix['2010-10-06']

    x, y = subset.index.to_series(), subset['glucose']

    # Basic plot setup
    plot = figure(plot_width=600, plot_height=300, x_axis_type="datetime", tools="",
                  toolbar_location=None, title='Hover over points')

    plot.line(x, y, line_dash="4 4", line_width=1, color='gray')

    cr = plot.circle(x, y, size=20,
                     fill_color="grey", hover_fill_color="firebrick",
                     fill_alpha=0.05, hover_alpha=0.3,
                     line_color=None, hover_line_color="white")

    plot.add_tools(HoverTool(tooltips=None, renderers=[cr], mode='hline'))

    # Generate the script and HTML for the plot
    script, div = components(plot)

    # CDN is the resource class that contains information
    # related to embedding Bokeh's Javascript and CSS

    # Return the webpage
    return """
    <!doctype html>
    <head>
        <title>My wonderful trigonometric webpage</title>
        {bokeh_css}
        {bokeh_js}
    </head>
    <body>
        <h1>Everyone loves trig!
        {div}
        {script}
    </body>
     """.format(script=script, div=div, bokeh_css=CDN.render_css(), bokeh_js=CDN.render_js())


if __name__ == "__main__":
    app.run()
