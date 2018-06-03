from flask import Flask
from flask import request
app = Flask(__name__)

@app.route('/')
def index():
    """
    context allows Flask to make certain variables
    globally accessible to a thread without interfering with
    other threads.
    Multi-threaded web servers starts a pool of threads and select
    a thread from the pool to handle each incoming request
    """
    # here the request object is a request context which encapsulates
    # the contents of a HTTP request sent by the client
    user_agent = request.headers.get("User-Agent")
    # '<p>Your browser is {}</p>'.format(user_agent)
    return app.url_map

@app.route('/user/<name>')
def user(name):
    return '<h1>Hello, {}!</h1>'.format(name)


if __name__ == '__main__':
    app.run(debug=True)
"""
Instead of doing app.run
We can do
export FLASK_APP=hello.py
export FLASK_DEBUG=1
flask run

The flask run commmand runs the application with the development
web server, additional argument includes -host
flask run --host 0.0.0.0
This enables other computers in the same network to connect as well
"""