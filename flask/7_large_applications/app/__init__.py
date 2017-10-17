"""
Before the application is created in a global scope,
although that is convenient, it has the drawback of
once we run the script, there is no way to apply
the configuration dynamically since the app has already
been created
"""
from flask import Flask
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from config import config


# create Flask extensions without
# the application, leaving them uninitialized
mail = Mail()
db = SQLAlchemy()
bootstrap = Bootstrap()


def create_app(config_name):
    """
    Explicitly initialize the app with the specified
    configuration setting
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    # ?? TODO : why do we need this
    config[config_name].init_app(app)

    db.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    return app
