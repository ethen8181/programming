from flask import Flask
from jwt_security import authenticate, identity
from resources.user import UserRegistor
from resources.item import Item, ItemList
from resources.store import Store, StoreList
from extensions import api, jwt, db


def create_app():
    app = Flask(__name__)
    app.secret_key = 'some secret key'

    # please refer to the following link as to why
    # https://stackoverflow.com/questions/33738467/how-do-i-know-if-i-can-disable-sqlalchemy-track-modifications
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'

    register_extension(app)
    return app


def register_extension(app):
    db.init_app(app)

    # the callbacks needs to be supplied before init_app
    jwt.identity_callback = identity
    jwt.authentication_callback = authenticate
    jwt.init_app(app)

    api.add_resource(Item, '/item/<string:name>')
    api.add_resource(ItemList, '/items')
    api.add_resource(Store, '/store/<string:name>')
    api.add_resource(StoreList, '/stores')
    api.add_resource(UserRegistor, '/register')
    api.init_app(app)


app = create_app()


@app.before_first_request
def create_table():
    db.create_all()


if __name__ == '__main__':
    app.run(port=5000, debug=True)
