"""
An example flask rest api that just returns a json payload
saying hello world when calling the root endpoint.

Examples
--------
python app.py

After that we can use the following curl request to test the endpoint.
curl -X GET http://127.0.0.1:8080/
"""
from flask import Flask
from flask_restful import Resource, Api


app = Flask(__name__)
api = Api(app)


class HelloWorld(Resource):

    def get(self):
        return {'message': 'Hello World'}


api.add_resource(HelloWorld, '/')


if __name__ == '__main__':
    app.run(port=8080)
