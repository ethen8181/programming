from datetime import datetime
from flask import current_app
from flaskblog import db, login_manager
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


@login_manager.user_loader
def load_user(user_id):
    """Boilerplate code to have the login_manager manage user session for us."""
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    """
    from flaskblog import db, User, Post

    # create the database, if it's sqlite, it would simply be stored as a file
    db.create_all()

    # add users to the database
    user1 = User(username='Ethen', email='gibberish@gmail.com', password='password')
    db.session.add(user1)
    user2 = User(username='JohnDoe', email='jd@gmail.com', password='password')
    db.session.add(user2)

    # commit the changes
    db.session.commit()

    # query all the user in from the database
    # the result is a list of User that we can then loop through
    # [User('Ethen', 'gibberish@gmail.com', 'default.jpg'),
    #  User('JohnDoe', 'jd@gmail.com', 'default.jpg')]
    User.query.all()

    # filter by the username and grab the first record
    user = User.query.filter_by(username='Ethen').first()

    # adding post for a specific user
    post1 = Post(title='blog1', content='First Post Content!', user_id=user.ids)
    post2 = Post(title='blog2', content='Second Post Content!', user_id=user.ids)
    db.session.add(post1)
    db.session.add(post2)
    db.session.commit()
    user.posts

    # get the user_id for the post
    post = Post.query.first()
    post.user_id

    # instead of just getting the user_id, we can access the backref attribute
    # to obtain the entire User for the post
    post.author

    # clear all the records
    db.drop_all()
    """
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    # user can start off with the default picture, thus we won't set unique = True
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)

    # backref, allows us to use the author attribute to access the user who
    # created the post when give a Post object, note that posts is not actually
    # a Column, it is running additional query underneath the hood to get all the posts
    # written by a user, thus we won't see this field in the database schema
    posts = db.relationship('Post', backref='author', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        """Returns a token and a user id payload"""
        serializer = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return serializer.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        serializer = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = serializer.loads(token)['user_id']
        except:
            return None

        return User.query.get(user_id)

    def __repr__(self):
        return "User('{}', '{}', '{}')".format(self.username, self.email, self.image_file)


class Post(db.Model):
    __tablename__ = 'post'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)

    # the User and Post model will have a one to many relationship,
    # because one user can have multiple posts, but a post can only have 1 author,
    # i.e. Post will be the child table
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return "Post('{}', '{}')".format(self.title, self.date_posted)
