#!/usr/bin/env python
"""
This file has two uses:
1) Run this file standalone via cron to update the db every five mins.
2) From webserver, call loadCurrentConditions periodically to get new data for the page
"""
import os
os.environ["RUNTIME_CONFIG"] = 'dev'

import arrow #http://crsmithdev.com/arrow/
import pickle
import json

from app import app, create_tables
from models import *
from wunderground import *

def loadCurrentConditions():
    "Load the current conditions from the file. Call this from webserver"
    fname = app.config.CONDITIONS_FILE
    try: # lead tho conditions object from previous call
        with open(fname,'r') as f:
            conditions = pickle.load(f)
    except: # no such file - create the inital obj
        conditions = CurrentConditions()
    return conditions

def updateConditions(conditions = None):
    "Load current conditions and update it & db"
    if not conditions:
        # load from the file
        conditions = loadCurrentConditions()
        # update with the current conditions from wunderground
        getWundergroundConditions(conditions)

    # save current conditions to DB if it is not already there (e.g. if wundeground station is down)
    if Condition.select().count():
        lastCond = Condition.select().order_by(Condition.id.desc()).get()
        lastTime = arrow.get(lastCond.when)
        currTime = arrow.get(conditions.when)
        if lastTime != currTime:
            conditions.saveToDb()
    else:
        conditions.saveToDb()

    # save the conditions to a file
    fname = app.config.CONDITIONS_FILE
    with open(fname, 'w') as f:
        pickle.dump(conditions, f)

    return conditions


if __name__ == '__main__': # allow funcs above to be imported as a module
    create_tables(db)
    cond = updateConditions()
    print "Conditions: "
    for key,val in cond.__dict__.items():
        print '  %s: %s' % (key, val)
    #print json.dumps(cond.__dict__, indent=1) # pretty print it
