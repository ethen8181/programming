"""
pip install flask-wtf
"""
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired
from flask import Flask, render_template, session, redirect, url_for, flash


# the app.config dictionary is a place
# to store configuration variables used by the application,
# the SECRET_KEY variable is a general purpose encryption key
# used by Flask and many of its extensions
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
bootstrap = Bootstrap(app)


class NameForm(FlaskForm):
    """
    Each web form is created by inheriting the FlaskForm class,
    the class defines the list of fields in the form, each
    represented by an object and each field can have a validators
    that checks whether the input is valid, e.g. InputRequired checks
    to ensure the input is not empty

    1. StringField represents an <input> tag with a type="text" attribute
    and SubmitField represents an <input> tag with a type="submit" attribute
    2. The first argument to the constructor is the label that will be used
    when rendering the form the HTML
    """
    name = StringField('What is your name?', validators = [InputRequired()])
    submit = SubmitField('Submit')


# the index function can now handle GET and POST request
# instead of just GET request, which is the default
@app.route('/', methods = ['GET', 'POST'])
def index():
    form = NameForm()
    # when the form is a valid submission
    # we can access the data for the name field
    if form.validate_on_submit():
        # session is a dicionary that the application can use
        # to store values that are remembered between request,
        # it is used here to store the name so the redirected
        # request can use it to build the actual response;
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            # the template also needs to render the flash
            # in the base.html template, we use a close button
            # with Boostrap style warning message, and
            # the "&times;" is rendered as a x in html, it is
            # used to mimick the cross button to close the warning message
            flash('Looks like you have changed your name!')

        # after storing the name we set the name back to a
        # clean state by setting it to an empty string
        session['name'] = form.name.data
        form.name.data = ''

        # redirect is a type of response that gives the browser
        # a new url from which to load the page. It's a best practice
        # for web applications to not leave a POST request as the last
        # request sent by the browser, as it may cause duplicated POST.
        # Thus the common pattern to handle this is the POST -> redirect -> GET

        # redirect takes the input url to redirect to as an
        # argument, the input url uses the url_for function, which
        # accepts an view function as the first argument and return
        # its url, this prevents dependency on the route
        # e.g. in this case the view function that handles the root is index
        return redirect(url_for('index'))

    # the form is rendered using bootstrap framework, e.g.
    # {% import "bootstrap/wtf.html" as wtf %}
    # {{ wtf.quick_form(form) }}
    return render_template('index.html', form = form, name = session.get('name'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug = True)
