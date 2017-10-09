import numpy as np
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from lime.lime_tabular import LimeTabularExplainer
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired
from flask import Flask, render_template, session, redirect, url_for, flash


app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
bootstrap = Bootstrap(app)


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators = [InputRequired()])
    submit = SubmitField('Submit')


@app.route('/', methods = ['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('Looks like you have changed your name!')

        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('index'))

    return render_template('index.html', form = form, name = session.get('name'))


@app.route("/simple.png")
def simple():
    iris = load_iris()
    X_train, X_test, y_train, y_test = train_test_split(
        iris.data, iris.target, test_size = 0.2)

    rf = RandomForestClassifier(n_estimators = 100)
    rf.fit(X_train, y_train)

    explainer = LimeTabularExplainer(
        X_train, feature_names = iris.feature_names,
        class_names = iris.target_names, discretize_continuous = True)

    i = np.random.randint(X_test.shape[0])
    exp = explainer.explain_instance(
        X_test[i], rf.predict_proba,
        num_features = X_test.shape[1], top_labels = 1)
    return exp.as_html()


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug = True)
