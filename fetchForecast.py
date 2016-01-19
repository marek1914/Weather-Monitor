#!/usr/bin/env python
"""
This file has two uses:
1) Run this file standalone via cron to update the forecast twice a day.
2) From webserver, call loadForecast periodically to get new data for the page

NOTE: Because the low temp is for the day following the actual forecast day, if we
      get the forecast after midnight, we won't have access to the forecast for that 
      morning. Therefore, we should get the forecast twice daily - 6am and 6pm.
"""
import os
os.environ["RUNTIME_CONFIG"] = 'dev'

import arrow #http://crsmithdev.com/arrow/
import pickle
import json

from flaskapp import app, create_tables
from models import *
from wunderground import *

def loadForecast():
    "Load the current forecasts from the file. Call this from webserver"
    fname = app.config['FORECAST_FILE']
    try: # lead tho forecasts object from previous call
        with open(fname,'r') as f:
            forecast = pickle.load(f)
    except: # no such file - create the inital obj
        forecast = None
    return forecast

def getLatestForecast():
    forecast = Forecast()
    "Load current forecasts and update it & db"
    forecast.setDaily(getWundergroundDailyForecasts())
    #forecast.setHourly(getWundergroundHourlyForecasts())

    # save the forecasts to a file
    fname = app.config['FORECAST_FILE']
    with open(fname, 'w') as f:
        pickle.dump(forecast, f)

    return forecast


if __name__ == '__main__': # allow funcs above to be imported as a module
    forecast = getLatestForecast()
    print "Daily Forecasts: "
    for fc in forecast.daily:
        for key,val in fc.__dict__.items():
            print '  %s: %s' % (key, val)
