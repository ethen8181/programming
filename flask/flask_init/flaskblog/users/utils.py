import os
import secrets
from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
from flaskblog import mail


def update_new_picture(form_picture, current_picture, output_size=(125, 125)):
    """
    Saves the user's updated profile picture under the static/profile_pics
    directory which is relative to the app's root path, delete the user's
    original profile picture if that picture is not the default picture for
    everyone at the beginning of signing up and return the picture's hexed filename.

    Parameters
    ----------
    form_picture :
        form.picture.data. Data from the UpdateAccountForm's picture field.

    current_picture :
        User's current image file.

    output_size : tuple of size 2, default (125, 125)
        The image will be resized before its being saved to reduce
        the browser's loading. As of today since under the main.css,
        we've set the .account-img's width and height to be both 125 px,
        thus there's no point today in uploading pictures bigger than that.

    Returns
    -------
    picture_file : str
        Instead of the original picture file name that was uploaded by the user,
        we use a random hex to replace the original filename. That way when storing
        the file, we won't run into issues when users uploads picture that happens
        to have the same filename.
    """
    random_hex = secrets.token_hex(8)
    _, file_extension = os.path.splitext(form_picture.filename)
    new_picture_file = random_hex + file_extension
    picture_base_path = os.path.join(current_app.root_path, 'static', 'profile_pics')
    picture_path = os.path.join(picture_base_path, new_picture_file)

    # the default image for everyone is the default.png as specified in the
    # User model's image_file field. Thus, we shouldn't delete it if that's
    # the user's current profile pic
    if current_picture != 'default.png':
        current_picture_path = os.path.join(picture_base_path, current_picture)
        os.remove(current_picture_path)

    image = Image.open(form_picture)
    image.thumbnail(output_size)
    image.save(picture_path)
    return new_picture_file


def send_password_reset_email(user):
    token = user.get_reset_token()
    message = Message(subject='Password Reset Request',
                      sender='noreply@demo.com',
                      recipients=[user.email])
    # _external=True the reset password link needs to be an absolute url
    # since it's connecting to the app from outside of this application
    link = url_for('reset_password_token', token=token, _external=True)
    body = ('To reset your password, visit the following link:\n'
            '{link}\n\n'
            'If you did not make this request, then simply ignore this email'
            'and no change will be made')
    body = body.format(link=link)
    message.body = body
    mail.send(message)
