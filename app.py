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
from flask.ext.sqlalchemy import SQLAlchemy

# config
DEBUG = True
PER_PAGE = 20
SECRET_KEY = "devopsborat"
PASSWORD = "default"

# make app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)
app.config.from_object(__name__)

def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)
app.jinja_env.globals['url_for_other_page'] = url_for_other_page


###
# Routing for your application.
###

@app.route('/')
def index():
    """Render website's home page."""
    return render_template('index.html')


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