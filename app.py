# app.py
# for info on setting up a flask & peewee app, see - http://charlesleifer.com/blog/saturday-morning-hack-a-little-note-taking-app-with-flask/

import os

from flask import Flask
#from peewee import SqliteDatabase
#from flask_peewee.db import Database # see - http://flask-peewee.readthedocs.org/en/latest/database.html

from settings import *


def create_tables(db):
    # Create table for each model if it does not exist.
    # Use the underlying peewee database object instead of the
    # flask-peewee database wrapper:
    from models import Condition, Environ, Record
    db.create_tables([Condition, Environ, Record], safe=True)

if "RUNTIME_CONFIG" in os.environ:
    runtime_config = os.environ["RUNTIME_CONFIG"]
else:
    runtime_config = 'dev'

if runtime_config == 'dev':
    config = DevelopmentConfig
elif runtime_config == 'prod':
    config = ProductionConfig
elif runtime_config == 'test':
    config = TestingConfig
else:
    config = DevelopmentConfig

app = Flask(__name__)
app.config.from_object(config) # magically imports all configs from settings. See - http://flask.pocoo.org/docs/0.10/config/
#db = SqliteDatabase(app.config['DATABASE'])
# instantiate the db wrapper
#db = Database(app)

