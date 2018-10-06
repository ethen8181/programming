import sqlite3
from flask_restful import Resource, reqparse


class User:

    def __init__(self, _id, username, password):
        self.id = _id
        self.username = username
        self.password = password

    @classmethod
    def find_by_username(cls, username):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "SELECT * FROM users WHERE username=?"
        result = cursor.execute(query, (username,))

        # either tuple or None
        row = result.fetchone()
        if row:
            user = cls(*row)
        else:
            user = None

        connection.close()
        return user

    @classmethod
    def find_by_id(cls, _id):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "SELECT * FROM users WHERE id=?"
        result = cursor.execute(query, (_id,))

        # either tuple or None
        row = result.fetchone()
        if row:
            user = cls(*row)
        else:
            user = None

        connection.close()
        return user


class UserRegistor(Resource):
    """
    use the /register endpoint to register a user,
    after registration we can use the /auth endpoint
    to retrieve the JWT token, which is required for
    the GET item endpoint.
    """

    parser = reqparse.RequestParser()
    parser.add_argument(
        'username', type=str, required=True,
        help='username must be passed with the payload')
    parser.add_argument(
        'password', type=str, required=True,
        help='password must be passed with the payload')

    def post(self):
        data = UserRegistor.parser.parse_args()

        username = data['username']
        if User.find_by_username(username):
            return {'message': 'A user with name {} already exists'.format(username)}, 400

        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        # the first column userid is auto-incrementing,
        # hence we can simply insert null
        query = "INSERT INTO users VALUES (NULL, ?, ?)"
        cursor.execute(query, (username, data['password']))

        connection.commit()
        connection.close()
        return {'message': 'User created successfully'}, 201
