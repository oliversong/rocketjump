"""
    Rocketjump
    ~~~~~~~~~~

    Ho ho ho.

    6.470.
"""

from __future__ import with_statement
import  time, os
from flask import Flask, render_template, request, redirect, url_for, abort, g, flash, escape, session
from werkzeug import check_password_hash, generate_password_hash
from datetime import datetime
from flask_oauth import OAuth
from flask.ext.sqlalchemy import SQLAlchemy

# config
DEBUG = True
PER_PAGE = 20
SECRET_KEY = "devopsborat"
FACEBOOK_APP_ID = '124499577716801'
FACEBOOK_APP_SECRET = '8f3dc21d612f5ef19dbc98221e1c7a0d'

# make app
app = Flask(__name__)
#heroku
#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
#local
app.debug = DEBUG
app.secret_key = SECRET_KEY
oauth = OAuth()
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/rocketjumpdb'
db = SQLAlchemy(app)
app.config.from_object(__name__)


facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=FACEBOOK_APP_ID,
    consumer_secret=FACEBOOK_APP_SECRET,
    request_token_params={'scope':'email,user_birthday,user_location,user_photos,publish_actions'}
    )

# many to many relationships

# a note can have many assets, and an asset can have many notes
assetTable = db.Table('assetTable',
    db.Column('note_id', db.Integer, db.ForeignKey('notes.id')),
    db.Column('asset_id', db.Integer, db.ForeignKey('assets.id'))
)

# a user can have many courses, and a course can have many users

# a user can have many lectures, and a lecture can have many users

# a user can have many notes, and a note can have many users

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    fid = db.Column(db.Integer, unique=True)
    name = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True)
    courses = db.relationship('Course', backref='users', lazy='dynamic')
    lectures = db.relationship('Lecture', backref='users', lazy='dynamic')
    notes = db.relationship('Note', backref='users', lazy='dynamics')

    def __init__(self, fid, name, email):
        self.fid = fid
        self.name = name
        self.email = email

    def __repr__(self):
        return '<Name %r>' % self.name

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(80))
    professor = db.Column(db.String(80))
    description = db.Column(db.String(3000))
    lectures = db.relationship('Lecture', backref='courses', lazy='dynamic')
    notes = db.relationship('Note', backref='courses', lazy='dynamic')
    user_id = db.Column(db.Integer, db.ForeignKey('users.fid'))

    def __init__(self, location, professor, description):
        self.location = location
        self.professor = professor
        self.description = description

class Lecture(db.Model):
    __tablename__ = 'lectures'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DATE)
    notes = db.relationship('Note', backref='lectures', lazy='dynamic')
    assets = db.relationship('Asset', backref='lectures', lazy='dynamic')
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.fid'))

    def __init__(self, date):
        self.date = date

class Note(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.DATETIME)
    content = db.Column(db.String(50000))
    assets = db.relationship('Asset', secondary=assetTable, backref=db.backref('notes', lazy='dynamic'))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    lecture_id = db.Column(db.Integer, db.ForeignKey('lectures.id'))
    collaborators = db.Column(db.Integer, db.ForeignKey('users.fid'))

    def __init__(self, datetime, content):
        self.datetime = datetime
        self.content = content

class Asset(db.Model):
    __tablename__ = 'assets'
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(500))
    author = db.Column(db.String(80))
    lecture_id = db.Column(db.Integer, db.ForeignKey('lectures.id'))

    def __init__(self, location, author):
        self.location = location
        self.author = author

def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)
app.jinja_env.globals['url_for_other_page'] = url_for_other_page


#app.before_request
def before_request():
    g.user = None
    if 'fid' in session:
        g.user = db.session.query(User).from_statement(
            "SELECT * FROM users where fid=:user_id").\
            params(user_id=session['fid']).all()[0]

###
# Routing for your application.
###

@app.route('/')
def index():
    """Render website's home page."""
    return render_template('index.html')

@app.route('/login')
def login():
    return facebook.authorize(callback=url_for('facebook_authorized',
        next=request.args.get('next') or request.referrer or None,
        _external=True))

@app.route('/login/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    if resp is None:
        error = 'Access denied: reason=%s error=%s' %(
            request.args['error_reason'],
            request.args['error_descriptions']
        )
        return render_template('home.html', error=error)
    xyz = (resp['access_token'], '')
    session['oauth_token'] = xyz
    me = facebook.get('/me')
    if not db.session.query(User).filter(User.fid==me.data['id']):
        newuser = User(me.data['id'],me.data['name'],me.data['email'])
        db.session.add(newuser)
        db.session.commit()
    flash('You were logged in')
    session['fid'] = me.data['id']
    return redirect(url_for('home'))

@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')

@app.route('/logout')
def logout():
    """Log out dat"""
    flash('You were logged out')
    session.pop('fid', None)
    return redirect(url_for('index'))

@app.route('/home/')
def home():
    raise Exception("hello")
    return render_template('home.html')

@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html')

@app.route('/robots.txt')
def robots():
    res = app.make_response('User-agent: *\nAllow: /')
    res.mimetype = 'text/plain'
    return res

###
# The functions below should be applicable to all Flask apps.
###

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=600'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)