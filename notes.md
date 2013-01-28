# Notes for rocketjumper

## Coffeescript compiler

To run:

	coffee -cw app.coffee

To put in background:

	ctrl-z
	bg 1

## Local Postgresql server

start:

	pg_ctl -D /usr/local/var/postgres -l /usr/local/var/postgres/server.log start

stop:

	pg_ctl -D /usr/local/var/postgres stop -s -m fast

Homebrew installed autostart to

	~/Library/LaunchAgents/homebrew.mxcl.postgresql.plist

But I deleted it to start and stop manually. I dunno.

Check status:

	pg_ctl -D /usr/local/var/postgres status

Find the postgres process:

	ps auxwww | grep postgres

Running pg on heroku

to install / make db:

	heroku addons:add heroku-postgresql:dev
	heroku pg:promote HEROKU_POSTGRESQL_COLOR
	heroku run python
	>>> from app import initdb
	>>> initdb()

pg db use:

	db.session.add(user)
	db.session.delete(user)
	User.query.all()
	db.session.commit()

make/drop tables

	python
	>>> from app import db
	>>> db.drop_all()
	>>> db.create_all()

	#if dependent, issue commands from psql
	psql rocketjumpdb
	>>> drop table blah_table cascade;
	>>> \d
	No relations found
	>>> \q

MYSQL db refresh:

	mysql -u root -p
	> password
	> show databases
	> use [database]
	> TRUNCATE TABLE [table]

MYSQL tunnel on cloudfoundry

	vmc tunnel goombadb

## Misc

Starting the server:

	foreman start


## EC2 setup with postgresql, flask, gunicorn, and nginx

Start:

	PYTHONPATH=/home/ubuntu/rocketjump/venv/lib/python2.7/site-packages gunicorn --access-logfile=access_logs --error-logfile=error_logs -D app:app 

Stop:

	ps -ax | grep gunicorn
	kill [pid]

Nginx reload:

	sudo nginx -s reload


## Game plan

Let's use the etherpad lite api to supply group note taking services. We can hook it up to the application with the pyetherpadlite client library. So far so good. We'll have to host our own etherpadlite server (nodejitsu?). After that we 