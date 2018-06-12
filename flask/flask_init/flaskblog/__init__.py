from flask import Flask
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flaskblog.config import Config


# needed to tell the login_manager the route for the login page
# the string is [users blueprint].[the login page's view];
# login_message_category is for making the message prettier with bootstrap's info
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
mail = Mail()
db = SQLAlchemy()
bcrypt = Bcrypt()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    mail.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    from flaskblog.main.routes import main
    from flaskblog.users.routes import users
    from flaskblog.posts.routes import posts
    from flaskblog.errors.handlers import errors
    app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(errors)
    return app
