from flask_jwt import JWT
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy


api = Api()
jwt = JWT()
db = SQLAlchemy()
