from flask_restful import Resource, reqparse
from models.user import UserModel


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
        if UserModel.find_by_username(username):
            message = 'A user with name {} already exists'.format(username)
            return {'message': message}, 400

        user = UserModel(**data)
        user.save_to_db()
        return {'message': 'User created successfully'}, 201
