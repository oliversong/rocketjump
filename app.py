"""
    Rocketjump
    ~~~~~~~~~~

    Ho ho ho.

    6.470.
"""
from __future__ import with_statement
import  time, os, sys, json
from flask import Flask, render_template, request, redirect, url_for, abort, g, flash, escape, session, make_response
from werkzeug import check_password_hash, generate_password_hash
from datetime import datetime
from flask_oauth import OAuth, OAuthException
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from py_etherpad import EtherpadLiteClient
from werkzeug.contrib.fixers import ProxyFix
from werkzeug.datastructures import CallbackDict
from flask.sessions import SessionInterface, SessionMixin
from itsdangerous import URLSafeTimedSerializer, BadSignature

# config
DEBUG = True
PER_PAGE = 20
SECRET_KEY = "devopsborat"

# etherpad api connection

# make app
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

# local configs
apiKey = "qSoNop1JjHxPQcJkv3L5rrmgBrqNgC1t"
FACEBOOK_APP_ID = '136661329828261'
FACEBOOK_APP_SECRET = 'd5be13df741b358d10a26aceeeff5dd0'
DOMAIN = '.testability.org'
pad = EtherpadLiteClient(apiKey,'http://0.0.0.0:9001/api')
padURL = 'http://pad.testability.org:9001/p/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/rocketjumpdb'

# EC2
# apiKey = "shoopdawoop"
# FACEBOOK_APP_ID = '124499577716801'
# FACEBOOK_APP_SECRET = '8f3dc21d612f5ef19dbc98221e1c7a0d'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://hello:shoopdawoop@localhost/rocketjumpdb'
# pad = EtherpadLiteClient(apiKey,'http://pad.notability.org/api')
# DOMAIN = '.notability.org'
# padURL = 'http://pad.notability.org/p/'

app.config['DEBUG'] = DEBUG
app.config['SECRET_KEY'] = SECRET_KEY
oauth = OAuth()
db = SQLAlchemy(app)

def initdb():
    db.drop_all()
    db.create_all()
    new1 = Course('6.470 - Web Programming Competition', 'Cool people', "MIT 6.470 is a web programming class and competition that takes place over the IAP period at MIT. We are student-run with generous support from professors, administrators, and external sponsors. This is our 5th year running the competition. We've made huge strides from the first time that 6.470 was run and look to make it even bigger and better this year.")
    new2 = Course('6.270 - Autonomous Robot Competition', 'Consult Department', "6.270 is a hands-on, learn-by-doing class open only to MIT students, in which participants design and build a robot that will play in a competition at the end of January. The goal is to design a machine that will be able to navigate its way around the playing surface, recognize other opponents, and manipulate game objects. Unlike the machines in Introduction to Design (formerly 2.70, now 2.007), 6.270 robots are totally autonomous, so once a round begins, there is no human intervention (in 2.007 the machines are controlled with joysticks).")
    new3 = Course('6.370 - Battlecode', 'Consult Department', "The 6.370 Battlecode programming competition is a unique challenge that combines battle strategy, software engineering and artificial intelligence. In short, the objective is to write the best player program for the computer game Battlecode.")
    new4 = Course('6.570 - Mobile App Competition', 'Consult Department', "6.570 is MIT's annual IAP Mobile Development Competition. Teams of 2-3 students will have 4 weeks to design and build an Android application. This year, it will run from January 7th - January 31st, 2013. The first two weeks of the competition will consist of lectures given both by students and leading industry experts, covering the basics of Android development, as well as other relevant concepts and tools, to help the participants build great apps. The contest will culminate in a public presentation by all teams in front of a judging panel comprised of MIT faculty and professional developers. Great prizes and everlasting fame will be awarded to the champions of 6.570!")
    new5 = Course('6.670 - iOS Game Competition', 'Consult Department', "Learn how to make iOS games, build an awesome game, and win cash prizes from sponsors like Playfirst, 500Startups, and Andreessen Horowitz!")
    db.session.add(new1)
    db.session.add(new2)
    db.session.add(new3)
    db.session.add(new4)
    db.session.add(new5)
    jsonData = open('dataset/IAPcourses.json')
    data = json.load(jsonData)
    jsonData.close()
    for item in data['items']:
        if item["type"]=="Class":
            course_name = item["id"]+' - '+item["shortLabel"]
            professor = "Unknown"
            if item["in-charge"] != "null":
                professor = item["in-charge"]
            elif item["fall_instructors"][0] != "":
                professor = item["fall_instructors"][0]
            elif item["spring_instructors"][0] != "":
                professor = item["spring_instructors"][0]
            description = item["description"]
            new = Course(course_name, professor, description)
            db.session.add(new)
    db.session.commit()

facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=FACEBOOK_APP_ID,
    consumer_secret=FACEBOOK_APP_SECRET,
    request_token_params={'scope':'email,user_birthday,user_education_history,user_photos,publish_actions'}
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
    fname = db.Column(db.String(80))
    lname = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True)
    picurl = db.Column(db.String(120))
    spicurl = db.Column(db.String(120))
    courses = db.relationship('Course', secondary=courseTable, backref=db.backref('users', lazy='dynamic'))
    lectures = db.relationship('Lecture', secondary=lectureTable, backref=db.backref('users', lazy='dynamic'))
    notes = db.relationship('Note', secondary=noteTable, backref=db.backref('users', lazy='dynamic'))
    queues = db.relationship('Queue', secondary=queueTable, backref=db.backref('users', lazy='dynamic'))
    authorID = db.Column(db.String(120), unique=True)
    sessionID = db.Column(db.String(120))
    college = db.Column(db.String(120))

    def __init__(self, fid, fname, lname, email, username, college):
        self.fid = fid
        self.fname = fname
        self.lname = lname
        self.email = email
        self.picurl = "http://graph.facebook.com/"+username+"/picture?width=200&height=200"
        self.spicurl = "https://graph.facebook.com/"+username+"/picture?type=square"
        self.authorID = pad.createAuthorIfNotExistsFor(fid,fname+' '+lname)['authorID']
        self.college = college

    def __repr__(self):
        return '<Name %r>' % self.fname+' '+self.lname

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    professor = db.Column(db.String(80))
    description = db.Column(db.String(3000))
    count = db.Column(db.Integer)
    lectures = db.relationship('Lecture', backref='course', lazy='dynamic')
    notes = db.relationship('Note', backref='course', lazy='dynamic')

    def __init__(self, name, professor, description):
        self.name = name
        self.professor = professor
        self.description = description
        self.count = 0

    def __repr__(self):
        return '<Name %r>' % self.name

class Lecture(db.Model):
    __tablename__ = 'lectures'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(120))
    notes = db.relationship('Note', backref='lecture', lazy='dynamic')
    assets = db.relationship('Asset', backref='lecture', lazy='dynamic')
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    queue = db.relationship('Queue', uselist=False, backref='lecture')
    live = db.Column(db.Boolean, default=False)
    groupID = db.Column(db.String(120), unique=True)

    def __init__(self, date, course):
        self.date = date
        self.course = course

    def __repr__(self):
        return '<Date %r>' % self.date

class Note(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    date = db.Column(db.String(120))
    assets = db.relationship('Asset', secondary=assetTable, backref=db.backref('notes', lazy='dynamic'))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    lecture_id = db.Column(db.Integer, db.ForeignKey('lectures.id'))
    public = db.Column(db.Boolean, default=False)
    url = db.Column(db.String(300))
    inProgress = db.Column(db.Boolean, default=False)
    liveCount = db.Column(db.Integer)

    def __init__(self, date, lecture, course, users):
        self.date = date
        self.lecture = lecture
        self.course = course
        self.name = 'Unnamed'
        self.users = users
        self.liveCount = 0


    def __repr__(self):
        return '<Name %r>' % self.name

class Queue(db.Model):
    __tablename__ = 'queues'
    id = db.Column(db.Integer, primary_key=True)
    lecture_id = db.Column(db.Integer, db.ForeignKey('lectures.id'))

    def __init__(self, lecture):
        self.lecture = lecture
        self.users = []

    def __repr__(self):
        return '<Queue %r>' % self.id

class Asset(db.Model):
    __tablename__ = 'assets'
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(500))
    author = db.Column(db.String(80))
    lecture_id = db.Column(db.Integer, db.ForeignKey('lectures.id'))

    def __init__(self, location, author, lecture):
        self.location = location
        self.author = author
        self.lecture = lecture

    def __repr__(self):
        return '<Asset %r>' % self.location

class ItsdangerousSession(CallbackDict, SessionMixin):

    def __init__(self, initial=None):
        def on_update(self):
            self.modified = True
        CallbackDict.__init__(self, initial, on_update)
        self.modified = False


class ItsdangerousSessionInterface(SessionInterface):
    salt = 'cookie-session'
    session_class = ItsdangerousSession

    def get_serializer(self, app):
        if not app.secret_key:
            return None
        return URLSafeTimedSerializer(app.secret_key, 
                                      salt=self.salt)

    def open_session(self, app, request):
        s = self.get_serializer(app)
        if s is None:
            return None
        val = request.cookies.get(app.session_cookie_name)
        if not val:
            return self.session_class()
        max_age = app.permanent_session_lifetime.total_seconds()
        try:
            data = s.loads(val, max_age=max_age)
            return self.session_class(data)
        except BadSignature:
            return self.session_class()

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        if not session:
            if session.modified:
                response.delete_cookie(app.session_cookie_name,
                                   domain=domain)
            return
        expires = self.get_expiration_time(app, session)
        val = self.get_serializer(app).dumps(dict(session))
        response.set_cookie(app.session_cookie_name, val,
                            expires=expires, httponly=True,
                            domain=domain)


def matchmake(lecture):

    # SHIIIEEET BLACK BOX ALGORITHM BRO
    if len(lecture.queue.users.all()) != 0:
        matched = lecture.queue.users.all().pop(0)
        db.session.commit()
        return matched 
    else:
        return None

def createPad(user,course,lecture):
    queue = lecture.queue.users.all()
    if user not in queue:
        queue.append(user)
    now = datetime.now()
    dt = now.strftime("%Y-%m-%d-%H-%M")
    # make new etherpad for user to wait in
    newNote = Note(dt, lecture, course, [user]) # init also creates a new pad at /p/groupID$noteID
    db.session.add(newNote)
    db.session.commit()
    pad.createGroupPad(newNote.lecture.groupID, newNote.id)
    newNote.url = padURL + lecture.groupID + "$" + str(newNote.id)
    db.session.commit()

    return newNote

def createLecture(user, course):
    # create new lecture
    now = datetime.now()
    dt = now.strftime("%Y-%m-%d-%H-%M")
    newLecture = Lecture(dt, course)
    db.session.add(newLecture)

    # add lecture to course, add new queue to lecture, add user to queue, add new user to lecture
    newQueue = Queue(newLecture)
    db.session.add(newQueue)
    db.session.commit()

    newLecture.users.append(user)
    newQueue.users.append(user)
    newLecture.groupID = pad.createGroupIfNotExistsFor(newLecture.course.name+dt)['groupID']

    db.session.commit()
    return newLecture

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

@app.errorhandler(OAuthException)
def handle_oauth_exception(error):
    # return an appropriate response
    print error.data
    print error.message
    print error.type
    return ':('

@app.route('/')
def index():
    """Render website's home page."""
    session['hi']='hi'
    return render_template('index.html')

@app.route('/login')
def login():
    return facebook.authorize(callback=url_for('facebook_authorized',
        next=request.args.get('next') or request.referrer or None,
        _external=True))

@app.route('/login/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    print 'hello'
    if resp is None:
        error = 'Access denied: reason=%s error=%s' %(
            request.args['error_reason'],
            request.args['error_descriptions']
        )
        print error
        return render_template('home.html', error=error)
    xyz = (resp['access_token'], '')
    session['oauth_token'] = xyz
    me = facebook.get('/me')
    print 'getting user'
    fid = me.data['id']
    print 'got fid', fid
    checkUser = db.session.query(User).filter(User.fid==fid).first()
    print 'got user from DB'
    if not checkUser:
        print 'no user yet'
        fname = me.data['name'].split()[0]
        lname = me.data['name'].split()[-1]
        education='Massachusetts Institute of Technology (MIT)'
        if 'education' in me.data:
            education=me.data['education'][-1]['school']['name']
        email = me.data['email']
        username = me.data['username']
        print fid, fname, lname, email, username, education
        newuser = User(fid, fname, lname, email, username, education)
        db.session.add(newuser)
        db.session.commit()
    print 'giving session token'
    session['fid'] = fid
    return redirect(url_for('home')) 

@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')

@app.route('/logout')
def logout():
    """Log out dat"""
    flash('You were logged out')
    session.pop('fid', None)
    resp = make_response(redirect(url_for('index')))
    resp.set_cookie('sessionID', '', expires=0, domain=DOMAIN)
    return resp

@app.route('/settings/')
def settings():
    if 'fid' not in session:
        flash('Please sign in.')
        return redirect(url_for('index'))
    return render_template('settings.html')

@app.route('/home/')
def home():
    if 'fid' not in session:
        flash('Please sign in.')
        return redirect(url_for('index'))
    collabs=[]
    curnotes = g.user.notes
    for note in g.user.notes:
        for user in note.users:
            if user != g.user:
                if user not in collabs:
                    collabs.append(user)
    possCourses= db.session.query(Course).order_by(desc(Course.count)).limit(3).all()
    suggested = []
    for c in possCourses:
        if g.user not in c.users:
            suggested.append(c) 
    # check for live notes
    unclosed=[]
    for x in g.user.notes:
        if x.inProgress:
            unclosed.append(x)
    return render_template('home.html', collaborators=collabs, suggested=suggested, unclosed=unclosed)

@app.route('/search')
def search():
    print "getting request"
    query = request.args['callback']
    print "this is the query:", query
    result = db.session.query(Course).filter(Course.name.like('%'+query+'%')).limit(10).all()
    result = [x.name for x in result]

    print "result", result
    return json.dumps(result)


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

@app.route('/<coursename>/', methods=['GET', 'POST'])
def course(coursename):
    """Course page"""
    courseobj = db.session.query(Course).filter(Course.name == coursename).all()
    if len(courseobj)==0:
        flash('No courses found by that name.')
        return redirect(url_for('home'))
    elif len(courseobj)>1:
        raise Exception('More than one course by that name...uh oh.')
    else:
        if request.method == 'POST':
            if 'fid' not in session:
                abort(401)
            g.user.courses.append(courseobj[0])
            db.session.commit()
            enrolled = True
        else:
            if courseobj[0] in g.user.courses:
                enrolled = True
            else:
                enrolled = False
        unotes = []
        unclosed=[]
        for x in g.user.notes:
            if x.course == courseobj[0]:
                if x.inProgress:
                    unclosed.append(x)
                unotes.append(x)
        live = False
        for lec in courseobj[0].lectures:
            if lec.live:
                live = True
        noPublic=True
        for y in courseobj[0].notes:
            if y.public:
                noPublic==False

    return render_template('course.html', course=courseobj[0], enrolled=enrolled, unclosed=unclosed, unotes=unotes, live=live, noPublic=noPublic)

@app.route('/<coursename>/match')
def match(coursename):
    if 'fid' not in session:
        abort(401)

    user = db.session.query(User).filter(User.fid == session['fid']).first()
    courseobj = db.session.query(Course).filter(Course.name == coursename).first()
    liveLectures = filter(lambda lecture: lecture.live == True, courseobj.lectures)
    print "hi"
    if len(liveLectures) == 0:
        print "course isn't live"

        # new lecture, new note
        newLecture = createLecture(user, courseobj)
        newNote = createPad(user, courseobj, newLecture)

        # make lecture live
        newNote.inProgress = True
        newLecture.live = True
        db.session.commit()
        newNote.liveCount += 1

        sessionID = pad.createSession(newNote.lecture.groupID, user.authorID, int(time.time() + 86400))['sessionID']
        user.sessionID = sessionID
        db.session.commit()
        return redirect(url_for('notepad', coursename=courseobj.name, noteid=newNote.id))

    elif len(liveLectures) == 1:
        print "course is live"
        # user may already be in an unclosed note
        if liveLectures[0] in user.lectures:
            for x in user.notes:
                if x.inProgress and x in liveLectures[0].notes:
                    print "this user has an unclosed note"
                    return redirect(url_for('notepad', coursename=courseobj.name, noteid=x.id))

        # user isn't in a note
        matchedUser = matchmake(liveLectures[0])
        if matchedUser != None:
            # user waiting; pair up; remove other user from queue
            print 'user waiting'
            liveLectures[0].queue.users.remove(matchedUser)
            note = matchedUser.notes[-1]
            user.notes.append(note)
            note.liveCount += 1
            db.session.commit()
            # everyone who is on the queue should already be in a pad, so just redirect the person to their note url
            sessionID = pad.createSession(note.lecture.groupID, user.authorID, int(time.time()+86400))['sessionID']
            user.sessionID = sessionID
            db.session.commit()
            return redirect(url_for('notepad', coursename=courseobj.name, noteid=note.id))

        else:
            # there is no user waiting; everyone is paired up
            # lecture already exists; create note and put user in it
            print 'no user waiting'
            newNote = createPad(user,courseobj,liveLectures[0])
            newNote.inProgress = True
            newNote.liveCount += 1
            db.session.commit()
            sessionID = pad.createSession(newNote.lecture.groupID, user.authorID, int(time.time()+86400))['sessionID']
            user.sessionID = sessionID
            db.session.commit()
            return redirect(url_for('notepad', coursename=courseobj.name, noteid=newNote.id))

    else:
        # dafuq
        abort(401)

@app.route('/<coursename>/<int:noteid>')
def notepad(coursename, noteid):
    if 'fid' not in session:
        abort(401)
    user = db.session.query(User).filter(User.fid == session['fid']).first()
    note = db.session.query(Note).filter(Note.id == noteid).first()
    note.inProgress = True
    note.lecture.live = True
    db.session.commit()
    if note not in user.notes:
        flash("Sorry, you're not part of that note!")
        redirect(url_for('home'))
    response = make_response(render_template('notepad.html',note=note))
    response.set_cookie('sessionID',user.sessionID, domain=DOMAIN)
    return response

@app.route('/<coursename>/<int:noteid>/done', methods=['GET','POST'])
def done(coursename, noteid):
    note = db.session.query(Note).filter(Note.id == noteid).first()
    if note not in g.user.notes:
        abort(401)
    note.liveCount -= 1
    if note.liveCount == 0:
        note.inProgress = False
    result = False
    for blah in note.lecture.notes:
        if blah.inProgress:
            result = True
    note.lecture.live = result
    db.session.commit()
    if request.method == 'GET':
        return redirect(url_for('home'))
    else:
        return 'done'

@app.route('/<coursename>/<int:noteid>/new', methods=['POST'])
def updateName(coursename,noteid):
    note = db.session.query(Note).filter(Note.id == noteid).first()
    note.name=request.form['newval']
    db.session.commit()
    return 'done'

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


app.session_interface = ItsdangerousSessionInterface()

if __name__ == '__main__':
    app.run(debug=True)
