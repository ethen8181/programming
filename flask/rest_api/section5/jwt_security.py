"""
Boilerplate code from Flask-JWT
https://pythonhosted.org/Flask-JWT/
"""
from user import User


def authenticate(username, password):
    """JWT authentication, receives the username and password
    returns an object representing an authenticated user."""
    user = User.find_by_username(username)
    if user and user.password == password:
        return user


def identity(payload):
    """Receives the JWT payload
    """
    user_id = payload['identity']
    return User.find_by_id(user_id)