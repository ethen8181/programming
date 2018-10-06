from flask import Flask
from flask_jwt import JWT
from flask_restful import Api, reqparse
from jwt_security import authenticate, identity
from user import UserRegistor
from item import Item, ItemList


app = Flask(__name__)
app.secret_key = 'some secret key'
api = Api(app)
jwt = JWT(app, authenticate, identity)

api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')
api.add_resource(UserRegistor, '/register')

if __name__ == '__main__':
    app.run(port=5000, debug=True)
