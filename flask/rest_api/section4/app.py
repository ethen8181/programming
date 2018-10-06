from flask import Flask
from flask_restful import Resource, Api, reqparse
from flask_jwt import JWT, jwt_required
from jwt_security import authenticate, identity


"""
Flask Restful limits the flexible we have with flask, but makes sure
our rest api is REST compliant.

The general workflow is to define our resource and the HTTP method
our resource accepts, and add the resource along with its url endpoint
to an API object.

Test Driven API
---------------
A good approach is to start from postman and write down the endpoint that
we will be exposing, the HTTP verbs allowed and the endpoint's corresponding
description.

JWT
---
Send encrypted message over the network, and the user won't be able to
decrypt the message unless they have a specify key.

flask_jwt's JWT will create a new endpoint /auth
when we call the endpoint, we send it a username and password, and JWT
will return us a token. Using that token, we can send it with the next request we make.
To elaborate, in the header, we need to specify
key: Authorization 
value: JWT [insert authorization token]

JWT in-depth
------------
Json Web Token is an open standard that defines a way for securely transmitting
information between parties as JSON object.

It is commonly used for authorization.
Once the user is logged in, each subsequent request will include the JWT,
allowing the user to access routes, resources that are permitted with that token.

a JWT is a string which takes the format of header.payload.signature

header: consists of the token type JWT and the hashing algorithm being used
Then this JSON is Base64Url encoded to form the header part. The hasing algorithm
uses a secret key to compute the signature.
payload: the data that's stored inside the JWT, this data is also referred to as
the claims to JWT. e.g. we can store the userId into the payload. (we can put
other claims as well), this will be Base64Url encoded as well
signature : HASH(header + '.' + payload, secret key), this verfies the message
wasn't changed along the way.

It is important to understand JWT are signed and encoded only, it does not
perform encryption, thus it does not guarantee any security for sensitive data.

As the JWT is signed by the algorithm where only the authentication
server knows the secret key, when we as a user, makes a JWT-attached API call
to the application, the server can verify the signature matches its hashing operation.

- https://medium.com/vandium-software/5-easy-steps-to-understanding-json-web-tokens-jwt-1164c0adfcec
- https://jwt.io/introduction/
"""
app = Flask(__name__)
app.secret_key = 'some secret key'
api = Api(app)
jwt = JWT(app, authenticate, identity)


items = [

]


class Item(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('price', type=float, required=True,
                        help='item price must be passed with the payload')

    # we no longer need jsonify as inheriting the Resource
    # class gives us that for free, and we can just return python dictionaries
    @jwt_required()
    def get(self, name):
        for item in items:
            if item['name'] == name:
                return {'item': item}

        # 404 not found
        return {'item': None}, 404

    def post(self, name):
        for item in items:
            if item['name'] == name:
                # 400 for bad request
                return {'message': 'An item with name {} already exists'.format(name)}, 400

        data = Item.parser.parse_args()
        item = {'name' : name, 'price': data['price']}
        items.append(item)

        # apart from 201 status code indicating CREATED,
        # there's also 202 status code indicating ACCEPTED,
        # in this case it means it might take a while before the object
        # is finally created, so we're making sure the client is aware of this delay.
        return item, 201

    def put(self, name):
        data = Item.parser.parse_args()

        exists = False
        for item in items:
            if item['name'] == name:
                item.update(data)
                exists = True
        
        if not exists:
            item = {'name': name, 'price': data['price']}
            items.append(item)

        return item

    def delete(self, name):
        global items
        items = [item for item in items if item['name'] != name]
        return {'message': 'Item deleted'}


class ItemList(Resource):

    def get(self):
        return {'items': items}


api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')


if __name__ == '__main__':
    app.run(port=5000, debug=True)
