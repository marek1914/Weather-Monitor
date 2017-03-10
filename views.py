import os
import arrow

from flask import render_template, jsonify, request, make_response

from flaskapp import app
from funcs import *
from models import *
from fetchConditions import loadCurrentConditions
from fetchForecast import loadForecast

'''
  when: 2016-01-16 07:35:47+00:00

  uv: 0
  solarradiation: None
  visibility: 16.1

  winddir: 16
  winddeg: 4
  windspeed: 0.0
  windgust: 1.9

  rainamt_prev: 0
  rainamt: 0
  rainrate: 0
'''

def getCurrentConditions():
  return loadCurrentConditions()

# ajax func - to be used to update periodically via jquery

@app.route('/lastupdate/')
def lastUpdate():
    cond = getCurrentConditions()
    return getTime(cond.when)

@app.route('/temperature/')
def currTemp():
    cond = getCurrentConditions()
    return jsonify(
      temperature=cond.getTemperature(),
      humidity = cond.humidity,
      heatindex = cond.getHeatIndex(),
      windchill = cond.getWindChill(),
      feel = cond.getRealFeel(),
      dewpoint = cond.getDewpoint(),
      rawdp = cond.getRawDewpoint()
    )

@app.route('/outlook/')
def outlook():
    cond = getCurrentConditions()
    pressTrend = cond.pressureTrend
    if pressTrend >= 0:
      pressTrend = '+%s' % pressTrend
    return jsonify(
      icon=cond.getIconUrl(),
      outlook = cond.outlook,
      pressure = cond.pressure,
      presstrend = pressTrend,
    )

@app.route('/wind/')
def wind():
    cond = getCurrentConditions()
    currdir = cond.getWindDirection()
    mindir, maxdir = cond.getWindDirRange()
    return jsonify(
      currdir=currdir,
      mindir = mindir,
      maxdir = maxdir,
      speed = cond.getWindSpeed(),
      gusts = cond.getWindGust(),
    )

@app.route('/rain/')
def rain():
    cond = getCurrentConditions()
    return jsonify(
      ratewg = getDistInUnits(cond.rainrate),
      rate = getDistInUnits(cond.getRainRate()),
      amt = getDistInUnits(cond.rainamt),
    )

@app.route('/hilo_temps/')
def hilow_temps():
  forecast = loadForecast()
  past1 = forecast.pastTemps[0]
  past2 = forecast.pastTemps[1]
  future1 = forecast.futureTemps[0]
  future2 = forecast.futureTemps[1]
  return jsonify(
    past1_label = past1.getLabel(),
    past1_value = past1.getValue(),
    past2_label = past2.getLabel(),
    past2_value = past2.getValue(),
    future1_label = future1.getLabel(),
    future1_value = future1.getValue(),
    future2_label = future2.getLabel(),
    future2_value = future2.getValue(),
  )

@app.route('/setunits/')
def setUnits():
  "Save post data for user preferred units"
  "See - http://flask.pocoo.org/docs/0.10/quickstart/#cookies"
  # resp = make_response(render_template(...))
  # resp.set_cookie('units_timp', unitsTemp)
  # return resp
  pass

@app.route('/')
def index():
    cond = getCurrentConditions()
    return render_template('index.html',
      #TODO - get rid of metric:
      metric = cond.metric,
      units_temp = getUnitsTemp(),
      units_dist = getUnitsDist(),
      units_speed = getUnitsSpeed(),
      units_pressure = getUnitsPressure(),
      hot = True if CtoF(cond.temperature) >= 75 else False,
    )
