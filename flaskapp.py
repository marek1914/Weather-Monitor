"""
Monitoring webserver starting point. 
Ref - http://flaskfiles.pocoo.org/docs/0.10/quickstart/

"""
import os

from flask import Flask

from settings import *


if "RUNTIME_CONFIG" in os.environ:
    runtime_config = os.environ["RUNTIME_CONFIG"]
else:
    runtime_config = 'dev'

#print 'run config: %s' % runtime_config

if runtime_config == 'dev':
    configobj = DevelopmentConfig
elif runtime_config == 'prod':
    configobj = ProductionConfig
elif runtime_config == 'test':
    configobj = TestingConfig
else:
    configobj = DevelopmentConfig


"""
Using 'app' instead of 'flaskApp' results in some confusion later on. It turns out that app.config
refers to the config object above (e.g. app.config.DEBUG) whereas app should refer to the app object
in which case it would be app.config['DEBUG'].

The solution is to change the name of this module to flaskapp and change config to configObj
TODO - refactor
"""
app = Flask(__name__)
app.config.from_object(configobj) # magically imports all configs from settings. See - http://flask.pocoo.org/docs/0.10/config/


def create_tables(db):
    # Create table for each model if it does not exist.
    # Use the underlying peewee database object instead of the
    # flask-peewee database wrapper:
    from models import Condition, Environ, Record
    db.create_tables([Condition, Environ, Record], safe=True)

def run():
    app.run(host='0.0.0.0', port=5002) # visible to network
    

