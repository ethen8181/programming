import os
from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog import db, bcrypt
from flaskblog.models import User, Post
from flaskblog.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                   RequestPasswordResetForm, ResetPasswordForm)
from flaskblog.users.utils import update_new_picture, send_password_reset_email


users = Blueprint('users', __name__)


@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!, You are now able to login', 'success')
        return redirect(url_for('users.login'))

    return render_template('register.html', title='Register', form=form)


@users.route("/login", methods=['GET', 'POST'])
def login():
    """
    The user will login with email and password, after successfully logged-in
    he/she will be send to the home page.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)

            # next_page:
            # when accessing a page that requires the user to be logged in (e.g. account page),
            # it will redirect the user back to the login page, after the user logs in, we
            # should send the user back the original page that he/she was trying to access.
            # flask will create a parameter 'next' in the url indicating the original url
            # that the user was trying to go on.
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')

    return render_template('login.html', title='Login', form=form)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    """
    The user needs to be logged-in in order to view the account page
    Note that login_required decorator must come first.
    """
    form = UpdateAccountForm()
    if form.validate_on_submit():
        # as specified in the UpdateAccountForm, the picture field
        # is not a required field when performing the update, thus
        # we should only take action when there is a new picture
        if form.picture.data:
            new_picture_file = update_new_picture(form.picture.data, current_user.image_file)
            current_user.image_file = new_picture_file

        current_user.email = form.email.data
        current_user.username = form.username.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        # when the user sees the account page, we can populate
        # the update account form with the user's current username
        # and email address instead of leaving it blank
        form.email.data = current_user.email
        form.username.data = current_user.username

    image_file = url_for('static', filename=os.path.join('profile_pics', current_user.image_file))
    return render_template('account.html', title='Account', image_file=image_file, form=form)


@users.route('/user/<string:username>')
def user_posts(username):
    """
    When clicking on the user name next to a post,
    we will show all the posts for a specific user.
    """
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = (Post.query.
             filter_by(author=user).
             order_by(Post.date_posted.desc()).
             paginate(per_page=5, page=page))

    return render_template('user_posts.html', posts=posts, user=user)


@users.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RequestPasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_password_reset_email(user)
        flash('An email has been sent with instruction to reset your password', 'info')
        return redirect(url_for('users.login'))

    return render_template('reset_password_request.html', title='Reset Password', form=form)


@users.route('/reset_password_token/<token>', methods=['GET', 'POST'])
def reset_password_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_password_request'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated!, You are now able to login', 'success')
        return redirect(url_for('users.login'))

    return render_template('reset_password_token.html', title='Reset Password', form=form)
