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
	>>> from app import db
	>>> db.create_all()

pg db use:

	db.session.add(user)
	db.session.delete(user)
	User.query.all()
	db.session.commit()

## Misc

Starting the server:

	foreman start
