import os
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired
from flask import Flask, render_template, session, redirect, url_for


basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')

# enable automatic commits of database changes at the end of each request
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# the db object instantiated from SQLAlchemy is the entry point to our database
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)


class Role(db.Model):
    """
    Model refers to the persistent entities used by the application.
    In this context of ORM (object relational mappers), which is a
    database abstraction layer that translates our operations to native
    database instruction, the model is represented as a class with
    attributes that match the table's column
    """

    # explicitly state the table name
    __tablename__ = 'roles'

    # first argument is the attribute's type, and the remaining
    # arguments specify configuration options for each attribute
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64), unique = True)

    # the users attribute represents the relationship, given
    # an instance of class Role, the users attribute will return
    # a list of users associated with that role. The first argument
    # to the .relationship method indicates what model is on the other
    # side of the relationship and it can be provided as a string if
    # the class is not defined yet. The backref argument specifies
    # the attribute for the reverse relationship
    users = db.relationship('User', backref = 'role', lazy = 'dynamic')

    def __repr__(self):
        return '<Role {}>'.format(self.name)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), unique = True, index = True)

    # defines the relationship between User and Role.
    # role_id column is the foreign key. role.id specifies
    # that column should be interpreted as having id values from
    # rows in the roles table (tablename)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User {}>'.format(self.username)


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators = [InputRequired()])
    submit = SubmitField('Submit')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/', methods = ['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        # access the query object to perform query on rows
        user = User.query.filter_by(username = form.name.data).first()
        if user is None:
            user = User(username = form.name.data)

            # changes to the database are manage through session.
            # the database session is not related to the Flask session,
            # this is often times referred to as a transaction
            db.session.add(user)

            # after writing the objects to the database, the session
            # needs to be committed, here we are leveraging the
            # SQLALCHEMY_COMMIT_ON_TEARDOWN configuration to automatically
            # perform the commit for us
            # db.session.commit()

            # a known session variable is used to customize the template
            session['known'] = False
        else:
            session['known'] = True

        session['name'] = form.name.data
        return redirect(url_for('index'))

    return render_template('index.html', form = form,
                           name = session.get('name'),
                           known = session.get('known', False))


if __name__ == '__main__':
    db.create_all()
    app.run()
