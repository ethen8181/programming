"""
Boilerplate code from Flask-JWT
https://pythonhosted.org/Flask-JWT/
"""
from user import User

users = [
    User(1, 'bob', 'asdf')
]

username_mapping = {user.username: user for user in users}
userid_mapping = {user.id: user for user in users}


def authenticate(username, password):
    """JWT authentication, receives the username and password
    returns an object representing an authenticated user."""
    user = username_mapping.get(username, None)
    if user and user.password == password:
        return user


def identity(payload):
    """Receives the JWT payload
    """
    user_id = payload['identity']
    return userid_mapping.get(user_id, None)