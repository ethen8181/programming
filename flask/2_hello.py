"""
python 1_hello.py

the web server should at the following url
http://127.0.0.1:5000/
"""
from flask import Flask

# all flask app must have an application instance
# as the web server passes all of its request to this
# object using a protocol called WSGI (web server gateway interface);
# the argument pass to Flask will be used to determine the root of
# the application so it can later find resource files
app = Flask(__name__)


# the application needs to know what code it needs to run for each
# URL requested, here if the user were to navigate to the home page
# on the browser, it would trigger to index function to run on the server
# and return the value (a.k.a response). Function such as index are referred
# to as a view function
@app.route('/')
def index():
    return '<h1>Hello World!</h1>'


# many url have variable sections, e.g. facebook/<username>
# the portion enclosed in the bracket, <>, is the dynamic part,
# dynamic component are string by default, but can be specified
# with a type, e.g. '/user/<int:id>'
@app.route('/user/<name>')
def user(name):
    return '<h1>Hello, {}!</h1>'.format(name)


if __name__ == '__main__':
    # the default web server provided by flask is not meant for production use
    app.run(debug = True)
