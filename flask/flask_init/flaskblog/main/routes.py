from flask import render_template, request, Blueprint
from flaskblog.models import Post

main = Blueprint('main', __name__)


@main.route('/')
@main.route('/home')
def home():
    """
    Show paginated posts posted by all the users (by paginated, we mean
    that we will only show 5 posts per page, 5 is a hard-coded value)

    we can replace the Post query with dummy data
    below to test application:

    posts = [
        {
            'author': 'Ethen Liu',
            'title': 'Blog Post 1',
            'content': 'First post content',
            'date_posted': 'April 20, 2018'
        },
        {
            'author': 'Jan Doe',
            'title': 'Blog Post 2',
            'content': 'Second post content',
            'date_posted': 'April 21, 2018'
        }
    ]
    """
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(per_page=5, page=page)
    return render_template('home.html', title="Homepage", posts=posts)


@main.route('/about')
def about():
    return render_template('about.html', title="About")
