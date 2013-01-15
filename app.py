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
from sqlalchemy import desc
from py_etherpad import EtherpadLiteClient

# config
DEBUG = True
PER_PAGE = 20
SECRET_KEY = "devopsborat"

# facebook api connection
FACEBOOK_APP_ID = '124499577716801'
FACEBOOK_APP_SECRET = '8f3dc21d612f5ef19dbc98221e1c7a0d'

# etherpad api connection
apiKey = "1zt8snBRk4XG242X4KfSOc0tcQSxH4vs"
pad = EtherpadLiteClient(apiKey,'http://0.0.0.0:9001/api')

# make app
app = Flask(__name__)
#heroku
#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
#local
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/rocketjumpdb'
app.debug = DEBUG
app.secret_key = SECRET_KEY
oauth = OAuth()
db = SQLAlchemy(app)
app.config.from_object(__name__)

def initdb():
    db.drop_all()
    db.create_all()
    newCourse = Course('6.470', '10-250', 'Oliver Song', 'osong@mit.edu', '6.470 is awesome!')
    db.session.add(newCourse)
    db.session.commit()

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
courseTable = db.Table('courseTable',
    db.Column('user_id', db.BigInteger, db.ForeignKey('users.id')),
    db.Column('course_id', db.Integer, db.ForeignKey('courses.id'))
)

# a user can have many lectures, and a lecture can have many users
lectureTable = db.Table('lectureTable',
    db.Column('user_id', db.BigInteger, db.ForeignKey('users.id')),
    db.Column('lecture_id', db.Integer, db.ForeignKey('lectures.id'))
)

# a user can have many notes, and a note can have many users
noteTable = db.Table('noteTable',
    db.Column('user_id', db.BigInteger, db.ForeignKey('users.id')),
    db.Column('note_id', db.Integer, db.ForeignKey('notes.id'))
)

# a user can be in many queues, and a queue can have many users
queueTable = db.Table('queueTable',
    db.Column('queue_id', db.Integer, db.ForeignKey('queues.id')),
    db.Column('user_id', db.BigInteger, db.ForeignKey('users.id'))
)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    fid = db.Column(db.BigInteger, unique=True)
    name = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True)
    picurl = db.Column(db.String(120))
    courses = db.relationship('Course', secondary=courseTable, backref='users')
    lectures = db.relationship('Lecture', secondary=lectureTable, backref='users')
    notes = db.relationship('Note', secondary=noteTable, backref='users')
    queues = db.relationship('MatchQueue', secondary=queueTable, backref='users')
    authorID = db.Column(db.String(120), unique=True)

    def __init__(self, fid, name, email, username):
        self.fid = fid
        self.name = name
        self.email = email
        self.picurl = "http://graph.facebook.com/"+username+"/picture?width=200&height=200"
        self.authorID = pad.createAuthorIfNotExistsFor(fid,name)['authorID']

    def __repr__(self):
        return '<Name %r>' % self.name

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    location = db.Column(db.String(80))
    professor = db.Column(db.String(80))
    profemail = db.Column(db.String(80))
    description = db.Column(db.String(3000))
    lectures = db.relationship('Lecture', backref='course', lazy='dynamic')
    notes = db.relationship('Note', backref='course', lazy='dynamic')
    count = db.Column(db.Integer)

    def __init__(self, name, location, professor, profemail, description):
        self.name = name
        self.location = location
        self.professor = professor
        self.profemail = profemail
        self.description = description
        self.count = 0

class Lecture(db.Model):
    __tablename__ = 'lectures'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(120))
    notes = db.relationship('Note', backref='lecture', lazy='dynamic')
    assets = db.relationship('Asset', backref='lecture', lazy='dynamic')
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    queue = db.relationship('MatchQueue', backref='lecture', lazy='dynamic')
    live = db.Column(db.Boolean, default=False)
    groupID = db.Column(db.BigInteger, unique=True)

    def __init__(self, date):
        self.date = date

class Note(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    date = db.Column(db.String(120))
    assets = db.relationship('Asset', secondary=assetTable, backref=db.backref('notes', lazy='dynamic'))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    lecture_id = db.Column(db.Integer, db.ForeignKey('lectures.id'))
    public = db.Column(db.Boolean, default=False)

    def __init__(self, date):
        self.date = date
        pad.createGroupPad(self.lecture.groupID,self.id)

class MatchQueue(db.Model):
    __tablename__ = 'queues'
    id = db.Column(db.Integer, primary_key=True)
    lecture_id = db.Column(db.Integer, db.ForeignKey('lectures.id'))

class Asset(db.Model):
    __tablename__ = 'assets'
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(500))
    author = db.Column(db.String(80))
    lecture_id = db.Column(db.Integer, db.ForeignKey('lectures.id'))

    def __init__(self, location, author):
        self.location = location
        self.author = author

def matchmake(lecture):
    # SHIIIEEET BLACK BOX ALGORITHM BRO
    if len(lecture.queue)!=0:
        return lecture.queue.pop(0)
    else:
        return None

def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)
app.jinja_env.globals['url_for_other_page'] = url_for_other_page


@app.before_request
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
    checkUser = db.session.query(User).filter(User.fid==me.data['id']).all()
    if not checkUser:

        newuser = User(me.data['id'],me.data['name'],me.data['email'],me.data['username'])
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

@app.route('/home')
def home():
    if 'fid' in session:
        curuser = db.session.query(User).from_statement(
            "SELECT * FROM users where fid=:user_id").\
            params(user_id=session['fid']).all()[0]
    else:
        flash('Please sign in.')
        return redirect(url_for('index'))
    collabs=[]
    curnotes = curuser.notes
    for note in curuser.notes:
        for user in note.users:
            if user != g.user:
                collabs.append(user)
    query = db.session.query(Course).order_by(desc(Course.count)).limit(3)
    suggested = query.all()
    return render_template('home.html', collaborators=collabs, suggested=suggested)

@app.route('/find', methods=['POST'])
def find():
    if request.method == 'POST':
        if not request.form['courseName']:
            error = 'You have to enter a course name'
            flash(error)
        else:
            #courseobj = db.session.query(Course).filter(Course.name==request.form['courseName']).all()
            return redirect(url_for('course', coursename=request.form['courseName']))
        return render_template('home.html')
    else:
        abort(404)

@app.route('/<coursename>', methods=['GET', 'POST'])
def course(coursename):
    """Course page"""
    courseobj = db.session.query(Course).filter(Course.name == coursename).all()
    if len(courseobj)==0:
        flash('No courses found by that name.')
        redirect(url_for('home'))
    elif len(courseobj)>1:
        raise Exception('More than one course by that name...uh oh.')
    else:
        if request.method == 'POST':
            if 'fid' not in session:
                abort(401)
            curuser = db.session.query(User).get(g.user.id)
            curcourse = db.session.query(Course).get(courseobj[0].id)
            curuser.courses.append(curcourse)
            db.session.commit()
            enrolled = True
        else:
            if courseobj[0] in g.user.courses:
                enrolled = True
            else:
                enrolled = False
    return render_template('course.html', course=courseobj[0], enrolled=enrolled)

def createPad(user,course,lecture):
    lecture.queue.users.append(user)
    # make new etherpad for user to wait in
    newNote = Note(dt) # init also creates a new pad at /p/groupID$noteID
    db.session.add(newNote)
    #db.session.commit()

    # add note to user, course, and lecture
    user.notes.append(newNote)
    course.notes.append(newNote)
    lecture.notes.append(newNote)
    db.session.commit()

    return newNote

def createLecture(user, course):
    # create new lecture
    now = datetime.now()
    dt = now.strftime("%Y-%m-%d-%H-%M")
    newLecture = Lecture(dt)
    db.session.add(newLecture)
    db.session.commit()

    # add lecture to course, add new queue to lecture, add user to queue
    newLecture.queue = MatchQueue()
    course.lectures.append(newLecture)
    newLecture.groupID = pad.createGroupIfNotExistsFor(newLecture.course.name+dt)['groupID']

    db.session.commit()
    return newLecture

@app.route('/<coursename>/match', methods=['GET','POST'])
def match(coursename):
    if request.method == 'POST':
        if 'fid' not in session:
            abort(401)


        user = db.session.query(User).filter(User.fid == session['fid']).all()[0]
        courseobj = db.session.query(Course).filter(Course.name == coursename).all()[0]
        #raise Exception("hi")
        liveLectures = filter(lambda lecture: lecture.live == True, courseobj.lectures)

        if len(liveLectures)==0:
            # course isn't live

            newLecture = createLecture(user, courseobj)

            # make new pad
            newNote = createPad(user,courseobj,newLecture)

            # make lecture live
            newLecture.live = True
            db.session.commit()

            redirect('http://0.0.0.0:9001/p/'+newLecture.groupID+"$"+newNote.id)

        elif len(liveLectures)==1:
            # course is live

            # do matchmaking, but there may not actually be a match
            matchedUser = matchmake(liveLectures[0])
            if matchedUser != None:
                # there is a user waiting; pair them up
                # remove other user from queue
                liveLectures[0].queue.remove(matchedUser)
                # add current user to note
                user.notes.append(matchedUser.notes[-1])
                # everyone who is on the queue should already be in a pad, so just redirect the person to their note url
                redirect('http://0.0.0.0:9001/p/'+liveLectures[0].groupID+"$"+matchedUser.notes[-1].id)
            else:
                # there is no user waiting; everyone is paired up
                # lecture already exists; create note and put user in it
                newNote = createPad(user,courseobj,liveLectures[0])
                redirect('http://0.0.0.0:9001/p/'+liveLectures[0].groupID+"$"+newNote.id)
        else:
            # dafuq
            abort(401)

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