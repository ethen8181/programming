"""
An application would often times require different
configuration settings, so here we
use classes to declare different configuration, e.g.
the need to use different databases for development,
testing and production so they won't interfere with
each other
"""
import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """
    TODO :
    declare if there's a need for ADMIN
    """
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    MAIL_SUBJECT_PREFIX = '[Flasky]'
    MAIL_SENDER = 'ethen8181@gmail.com'
    ADMIN = os.environ.get('ADMIN') or 'ethen8181@gmail.com'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig:
    DEBUG = True
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DEV_DATABASE_URL') or
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite'))


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('TEST_DATABASE_URL') or
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite'))


class ProductionConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DATABASE_URL') or
        'sqlite:///' + os.path.join(basedir, 'data.sqlite'))


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
