import os
from flask_wtf import FlaskForm
from flask_mail import Mail, Message
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired
from flask import Flask, render_template, session, redirect, url_for


basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


app.config['MAIL_SERVER'] = 'smtp.googlemail.com'

# port number should be 587 to match the MAIL_USE_TLS = True
# configuration below
# https://stackoverflow.com/questions/17404854/sending-mail-with-flask-mail
app.config['MAIL_PORT'] = 587

# enable Transport Layer Security, which is the crytographic
# protocol that provide communication security over a computer network
app.config['MAIL_USE_TLS'] = True
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['SECURITY_EMAIL_SENDER'] = 'ethen8181@gmail.com'

# note that if we're using gmail, then
# we have to turn on allowing less secure apps to sign in
# https://stackoverflow.com/questions/26852128/smtpauthenticationerror-when-sending-mail-using-gmail-and-python
# need to declare the environment variable
# export FLASKY_ADMIN=[email address]@gmail.com
# export MAIL_USERNAME=XXXXX
# export MAIL_PASSWORD=XXXXX
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')

db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
mail = Mail(app)


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64), unique = True)
    users = db.relationship('User', backref = 'role', lazy = 'dynamic')

    def __repr__(self):
        return '<Role {}>'.format(self.name)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), unique = True, index = True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User {}>'.format(self.username)


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators = [InputRequired()])
    submit = SubmitField('Submit')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


def send_email(subject, to, template, username):
    msg = Message(subject = app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  recipients = [to],
                  sender = app.config['SECURITY_EMAIL_SENDER'])
    msg.body = render_template(template + '.txt', username = username)
    msg.html = render_template(template + '.html', username = username)
    mail.send(msg)


@app.route('/', methods = ['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.name.data).first()
        if user is None:
            user = User(username = form.name.data)
            db.session.add(user)
            session['known'] = False

            if 'FLASKY_ADMIN' in app.config:
                send_email(subject = 'New User', to = app.config['FLASKY_ADMIN'],
                           template = os.path.join('mail', 'new_user'),
                           username = user.username)
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
