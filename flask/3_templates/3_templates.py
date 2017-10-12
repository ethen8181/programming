"""
pip install flask-bootstrap
"""

from flask import Flask, render_template
from flask_bootstrap import Bootstrap
app = Flask(__name__)

# the obvious task of a view function is to generate
# a response for a request, for response that are more
# complex, it's best to utilize Jinja templates to improve the
# maintainability of the code base;
# by default Flask looks for the templates in the templates
# subfolder, located in the application folder

# Bootstrap is an open-source framework that provides
# clean web user interface, a quick way to integrate
# Bootstrap with our application is to use a Flask
# extension called Flask-Bootstrap, once included
# a base template that includes all the Bootstrap file
# becomes available to the application, and we can take
# advantage of Jinja's inheritance feature
# http://jinja.pocoo.org/docs/2.9/templates/#template-inheritance;

# base template defines blocks that can be overriden by derived templates
# in the user.html template, the title, navbar and content are all blocks
# that the flask-bootstrap base template exports for derived templates to define
# https://pythonhosted.org/Flask-Bootstrap/basic-usage.html#available-blocks

# bootstrap notes:
# https://www.w3schools.com/bootstrap/bootstrap_navbar.asp
# 1. insert navgiation bar with
# <div class="navbar navbar-inverse" role="navigation">
# the navbar-inverse class defines a black navigation bar
# 2. <a> tag defines a hyperlink and the href attribute
# defines the link's destination
# 3. navbar-brand class defines the main button and
# nav navbar-nav class defines the sub-button
bootstrap = Bootstrap(app)


# here we modified the original 1_hello.py to utilize templates
# the render_template function takes the .html templates as
# the first argument, and any other additional variables are
# specified with a key value pair keyword argument
@app.route('/')
def index():
    return render_template('index.html')


# for the name variable that is used here, Jinja will look for the
# {{ name }} placeholder and replace it with the value provided
# at the time the template is rendered
@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name = name)


# when we enter an invalid route in the app's address bar, we get a
# code 404 error, with Flask we can define our custom error page.
# Here the return type is a tuple that contains the rendered template
# and the numeric status code, the default numeric status code is 200,
# which indicates a success
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug = True)
