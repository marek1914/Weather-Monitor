import arrow

from flask import request

from flaskapp import app

def rint(num):
  "Given float, return it rounded to nearest int"
  return int(round(num))
  
def CtoF(degC):
    return 32 + (1.8 * degC)

def FtoC(degF):
    return (degF - 32) / 1.8

def getUnitsTemp():
  return request.cookies.get('units_temp', app.config['UNITS_TEMP'])

def getUnitsDist():
  return request.cookies.get('units_dist', app.config['UNITS_DIST'])

def getUnitsSpeed():
  return request.cookies.get('units_speed', app.config['UNITS_SPEED'])

def getUnitsPressure():
  return request.cookies.get('units_pressure', app.config['UNITS_PRESSURE'])

def getTemperatureInUnits(degC):
    units = getUnitsTemp()
    return degC if units == 'C' else CtoF(degC)

def getDistInUnits(dist):
  units = getUnitsDist()
  if units == 'in':
    return dist * 25.4
  else:
    return dist # mm
    
def getSpeedInUnits(speed):
    units = getUnitsSpeed()
    if units == 'mph':
      return speed * 0.62;
    elif units == 'knots':
      return speed * 0.54;
    else:
      return speed # kph

def getPressureInUnits(pressure):
    units = getUnitsPressure()
    if units == 'mb':
      return pressure
    else:
      return pressure

def getTime(when):
  when = arrow.get(when) # convert
  timeOnly = arrow.utcnow().date() == when.date()
  when = when.to(app.config['TIMEZONE']) # localize
  if timeOnly:
    return when.format('h:mma')
  else:
    return when.format('YY-MM-DD h:mma')

def getColorLevel(amt, lvlG=50, lvlY=75):
    "Return color according to percentage level"
    if amt < lvlG:
        return 'green'
    elif amt < lvlY:
        return 'yellow'
    else:
        return 'red'
