import requests
import json

from models import *

WUG_KEY = 'f843bbca5bf0222c'

WUG_ROOT = 'http://api.wunderground.com/api/'

LOCATION = 'KY/Mount_Hermon'

# types of requests
CONDITIONS = 'conditions'
ASTRONOMY = 'astronomy'
RECORDS = 'almanac'
FORECAST = 'forecast'
FORECAST10DAY = 'forecast10day'


def fetchWundergroundData(requestType):
  "Query the Wundeground api"
  r = requests.get('{root}{key}/{request}/q/{loc}.json'.format(root=WUG_ROOT, key=WUG_KEY, loc=LOCATION, request=requestType))
  if r.status_code == 200:
    return r.json()
  else:
    return None


def convertWundergroundTimestamp(ts):
  "WU dt is in rfc822 format - # e.g. u'Thu, 24 Dec 2015 01:58:29 -0600'"
  from email.utils import mktime_tz, parsedate_tz
  from arrow import get as arrowget   # http://crsmithdev.com/arrow/
  # from datetime import datetime
  # from pytz import utc
  return arrowget(mktime_tz(parsedate_tz(ts))).datetime
  # return datetime.fromtimestamp(mktime_tz(parsedate_tz(ts)), utc)

def getWundergroundConditions(cond):
  "Given CurrentConditions obj, save wundeground data to it"
  res = fetchWundergroundData(CONDITIONS)
  res = res['current_observation'] # deferefence

  cond.setTimestamp(convertWundergroundTimestamp(res['observation_time_rfc822']))
  cond.setTemperature(float(res['temp_c']))
  cond.setPressure(int(res['pressure_mb']))
  #cond.setPressureTrend(int(res['pressure_trend']))
  cond.setHumidity(int(res['relative_humidity'][:-1]))
  cond.setWind(res['wind_degrees'], float(res['wind_kph']), float(res['wind_gust_kph']))
  cond.setRain(int(float(res['precip_1hr_in'])*25.4), int(float(res['precip_today_in'])*25.4)) # setRain keeps a running difference

  cond.setIcon(res['icon']) # cloudy
  cond.setOutlook(res['weather']) # eg Overcast
  try: # may be u'NA'
    hi = int(res['heat_index_c'])
  except:
    hi = None
  cond.setHeatIndex(hi)
  cond.setWindChill(int(res['windchill_c']))
  cond.setRealFeel(int(res['feelslike_c']))
  cond.setDewpoint(res['dewpoint_c'])

  cond.setUV(int(res['UV']))
  try:
    sr = int(res['solarradiation'])
  except:
    sr = None
  cond.setSolarRadiation(sr)
  cond.setVisibility(float(res['visibility_km']))

  #cond.setLeafmoisture()
  #cond.setLightning()


'''

// astronomical

res = res['moon_phase']


def getWGAstroTime(resp):
  return resp['hour'] + ':' + resp['minute']

// moon
moonPhase = res['ageOfMoon']
moonRise = getWGAstroTime(res['moonrise'])
moonSet = getWGAstroTime(res['moonset'])
moonIllumination = res['percentIlluminated']
moonPhaseStr = res['phaseofMoon']

// sun
sunrise = getWGAstroTime(res['sunrise'])
sunset = getWGAstroTime(res['sunset'])
'''

def getWundergroundForecastForDay(res):
  "Save wundeground forecast for the given day"
  fc = DailyForecast()
  fc.setTimestamp(res['date']['epoch'])
  fc.setLow(int(res['low']['celsius']))
  fc.setHigh(int(res['high']['celsius']))
  fc.setWind(res['maxwind']['kph'], res['maxwind']['degrees'])
  return fc

def getWundergroundDailyForecasts():
  "save wundeground forecast for given day (0 - 9)"
  res = fetchWundergroundData(FORECAST10DAY)
  res = res['forecast']['simpleforecast']['forecastday'] # deferefence
  forecasts = []
  for fc in res:
    forecasts.append(getWundergroundForecastForDay(fc))
  return forecasts


'''
// forecast

res['forecast']['simpleforecast']['forecastday'][0]
len(res['forecast']['simpleforecast']['forecastday'])
datestr = res['forecast']['simpleforecast']['forecastday'][1]['date']['epoch']
low = res['forecast']['simpleforecast']['forecastday'][0]['low']['celsius']
high = res['forecast']['simpleforecast']['forecastday'][0]['high']['celsius']
windspeed = res['forecast']['simpleforecast']['forecastday'][0]['maxwind']['kph']
winddir = res['forecast']['simpleforecast']['forecastday'][0]['maxwind']['degrees']
percip_day = res['forecast']['simpleforecast']['forecastday'][0]['qpf_day']['mm']
percip_night = res['forecast']['simpleforecast']['forecastday'][0]['qpf_night']['mm']
snow_day = res['forecast']['simpleforecast']['forecastday'][0]['snow_day']['cm']
snow_night = res['forecast']['simpleforecast']['forecastday'][0]['snow_night']['cm']


output for res['forecast']['simpleforecast']['forecastday'][0]:
{u'avehumidity': 90,
 u'avewind': {u'degrees': 14, u'dir': u'NNE', u'kph': 0, u'mph': 0},
 u'conditions': u'Overcast',
 u'date': {u'ampm': u'PM',
  u'day': 16,
  u'epoch': u'1452992400',
  u'hour': 19,
  u'isdst': u'0',
  u'min': u'00',
  u'month': 1,
  u'monthname': u'January',
  u'monthname_short': u'Jan',
  u'pretty': u'7:00 PM CST on January 16, 2016',
  u'sec': 0,
  u'tz_long': u'America/Chicago',
  u'tz_short': u'CST',
  u'weekday': u'Saturday',
  u'weekday_short': u'Sat',
  u'yday': 15,
  u'year': 2016},
 u'high': {u'celsius': u'2', u'fahrenheit': u'37'},
 u'icon': u'cloudy',
 u'icon_url': u'http://icons.wxug.com/i/c/k/cloudy.gif',
 u'low': {u'celsius': u'-5', u'fahrenheit': u'23'},
 u'maxhumidity': 0,
 u'maxwind': {u'degrees': 0, u'dir': u'', u'kph': 11, u'mph': 7},
 u'minhumidity': 0,
 u'period': 1,
 u'pop': 0,
 u'qpf_allday': {u'in': 0.0, u'mm': 0},
 u'qpf_day': {u'in': None, u'mm': None},
 u'qpf_night': {u'in': 0.0, u'mm': 0},
 u'skyicon': u'',
 u'snow_allday': {u'cm': 0.0, u'in': 0.0},
 u'snow_day': {u'cm': None, u'in': None},
 u'snow_night': {u'cm': 0.0, u'in': 0.0}}


"conditions"
{u'current_observation': {u'UV': u'0',
  u'dewpoint_c': 15,
  u'dewpoint_f': 59,
  u'dewpoint_string': u'59 F (15 C)',
  u'display_location': {u'city': u'Mount Hermon',
   u'country': u'US',
   u'country_iso3166': u'US',
   u'elevation': u'254.00000000',
   u'full': u'Mount Hermon, KY',
   u'latitude': u'36.83283234',
   u'longitude': u'-85.84632874',
   u'magic': u'1',
   u'state': u'KY',
   u'state_name': u'Kentucky',
   u'wmo': u'99999',
   u'zip': u'42157'},
  u'estimated': {},
  u'feelslike_c': u'16.8',
  u'feelslike_f': u'62.3',
  u'feelslike_string': u'62.3 F (16.8 C)',
  u'forecast_url': u'http://www.wunderground.com/US/KY/Mount_Hermon.html',
  u'heat_index_c': u'NA',
  u'heat_index_f': u'NA',
  u'heat_index_string': u'NA',
  u'history_url': u'http://www.wunderground.com/weatherstation/WXDailyHistory.asp?ID=KKYTEMPL1',
  u'icon': u'cloudy',
  u'icon_url': u'http://icons.wxug.com/i/c/k/nt_cloudy.gif',
  u'image': {u'link': u'http://www.wunderground.com',
   u'title': u'Weather Underground',
   u'url': u'http://icons.wxug.com/graphics/wu2/logo_130x80.png'},
  u'local_epoch': u'1450943950',
  u'local_time_rfc822': u'Thu, 24 Dec 2015 01:59:10 -0600',
  u'local_tz_long': u'America/Chicago',
  u'local_tz_offset': u'-0600',
  u'local_tz_short': u'CST',
  u'nowcast': u'',
  u'ob_url': u'http://www.wunderground.com/cgi-bin/findweather/getForecast?query=36.899570,-85.878143',
  u'observation_epoch': u'1450943909',
  u'observation_location': {u'city': u'Scout Reservation, Temple Hill',
   u'country': u'US',
   u'country_iso3166': u'US',
   u'elevation': u'780 ft',
   u'full': u'Scout Reservation, Temple Hill, Kentucky',
   u'latitude': u'36.899570',
   u'longitude': u'-85.878143',
   u'state': u'Kentucky'},
  u'observation_time': u'Last Updated on December 24, 1:58 AM CST',
  u'observation_time_rfc822': u'Thu, 24 Dec 2015 01:58:29 -0600',
  u'precip_1hr_in': u'0.00',
  u'precip_1hr_metric': u' 0',
  u'precip_1hr_string': u'0.00 in ( 0 mm)',
  u'precip_today_in': u'0.00',
  u'precip_today_metric': u'0',
  u'precip_today_string': u'0.00 in (0 mm)',
  u'pressure_in': u'29.73',
  u'pressure_mb': u'1007',
  u'pressure_trend': u'0',
  u'relative_humidity': u'88%',
  u'solarradiation': u'--',
  u'station_id': u'KKYTEMPL1',
  u'temp_c': 16.8,
  u'temp_f': 62.3,
  u'temperature_string': u'62.3 F (16.8 C)',
  u'visibility_km': u'16.1',
  u'visibility_mi': u'10.0',
  u'weather': u'Overcast',
  u'wind_degrees': 221,
  u'wind_dir': u'SW',
  u'wind_gust_kph': u'7.4',
  u'wind_gust_mph': u'4.6',
  u'wind_kph': 2.9,
  u'wind_mph': 1.8,
  u'wind_string': u'From the SW at 1.8 MPH Gusting to 4.6 MPH',
  u'windchill_c': u'NA',
  u'windchill_f': u'NA',
  u'windchill_string': u'NA'},
 u'response': {u'features': {u'conditions': 1},
  u'termsofService': u'http://www.wunderground.com/weather/api/d/terms.html',
  u'version': u'0.1'}}


"Astronomy"
{u'moon_phase': {u'ageOfMoon': u'14',
  u'current_time': {u'hour': u'2', u'minute': u'01'},
  u'hemisphere': u'North',
  u'moonrise': {u'hour': u'16', u'minute': u'16'},
  u'moonset': {u'hour': u'5', u'minute': u'45'},
  u'percentIlluminated': u'98',
  u'phaseofMoon': u'Waxing Gibbous',
  u'sunrise': {u'hour': u'6', u'minute': u'53'},
  u'sunset': {u'hour': u'16', u'minute': u'32'}},
 u'response': {u'features': {u'astronomy': 1},
  u'termsofService': u'http://www.wunderground.com/weather/api/d/terms.html',
  u'version': u'0.1'},
 u'sun_phase': {u'sunrise': {u'hour': u'6', u'minute': u'53'},
  u'sunset': {u'hour': u'16', u'minute': u'32'}}}

"almanac"
{u'almanac': {u'airport_code': u'KGLW',
  u'temp_high': {u'normal': {u'C': u'6', u'F': u'44'},
   u'record': {u'C': u'21', u'F': u'71'},
   u'recordyear': u'1964'},
  u'temp_low': {u'normal': {u'C': u'-2', u'F': u'27'},
   u'record': {u'C': u'-22', u'F': u'-8'},
   u'recordyear': u'1989'}},
 u'response': {u'features': {u'almanac': 1},
  u'termsofService': u'http://www.wunderground.com/weather/api/d/terms.html',
  u'version': u'0.1'}}


"Forecast"
{u'forecast': {u'simpleforecast': {u'forecastday': [{u'avehumidity': 69,
     u'avewind': {u'degrees': 159, u'dir': u'SSE', u'kph': 10, u'mph': 6},
     u'conditions': u'Clear',
     u'date': {u'ampm': u'PM',
      u'day': 24,
      u'epoch': u'1451005200',
      u'hour': 19,
      u'isdst': u'0',
      u'min': u'00',
      u'month': 12,
      u'monthname': u'December',
      u'monthname_short': u'Dec',
      u'pretty': u'7:00 PM CST on December 24, 2015',
      u'sec': 0,
      u'tz_long': u'America/Chicago',
      u'tz_short': u'CST',
      u'weekday': u'Thursday',
      u'weekday_short': u'Thu',
      u'yday': 357,
      u'year': 2015},
     u'high': {u'celsius': u'22', u'fahrenheit': u'71'},
     u'icon': u'clear',
     u'icon_url': u'http://icons.wxug.com/i/c/k/clear.gif',
     u'low': {u'celsius': u'15', u'fahrenheit': u'59'},
     u'maxhumidity': 0,
     u'maxwind': {u'degrees': 159, u'dir': u'SSE', u'kph': 16, u'mph': 10},
     u'minhumidity': 0,
     u'period': 1,
     u'pop': 0,
     u'qpf_allday': {u'in': 0.06, u'mm': 2},
     u'qpf_day': {u'in': 0.0, u'mm': 0},
     u'qpf_night': {u'in': 0.06, u'mm': 2},
     u'skyicon': u'',
     u'snow_allday': {u'cm': 0.0, u'in': 0.0},
     u'snow_day': {u'cm': 0.0, u'in': 0.0},
     u'snow_night': {u'cm': 0.0, u'in': 0.0}},
    {u'avehumidity': 87,
     u'avewind': {u'degrees': 149, u'dir': u'SSE', u'kph': 13, u'mph': 8},
     u'conditions': u'Rain',
     u'date': {u'ampm': u'PM',
      u'day': 25,
      u'epoch': u'1451091600',
      u'hour': 19,
      u'isdst': u'0',
      u'min': u'00',
      u'month': 12,
      u'monthname': u'December',
      u'monthname_short': u'Dec',
      u'pretty': u'7:00 PM CST on December 25, 2015',
      u'sec': 0,
      u'tz_long': u'America/Chicago',
      u'tz_short': u'CST',
      u'weekday': u'Friday',
      u'weekday_short': u'Fri',
      u'yday': 358,
      u'year': 2015},
     u'high': {u'celsius': u'19', u'fahrenheit': u'67'},
     u'icon': u'rain',
     u'icon_url': u'http://icons.wxug.com/i/c/k/rain.gif',
     u'low': {u'celsius': u'18', u'fahrenheit': u'64'},
     u'maxhumidity': 0,
     u'maxwind': {u'degrees': 149, u'dir': u'SSE', u'kph': 16, u'mph': 10},
     u'minhumidity': 0,
     u'period': 2,
     u'pop': 90,
     u'qpf_allday': {u'in': 1.79, u'mm': 45},
     u'qpf_day': {u'in': 0.95, u'mm': 24},
     u'qpf_night': {u'in': 0.84, u'mm': 21},
     u'skyicon': u'',
     u'snow_allday': {u'cm': 0.0, u'in': 0.0},
     u'snow_day': {u'cm': 0.0, u'in': 0.0},
     u'snow_night': {u'cm': 0.0, u'in': 0.0}},
    {u'avehumidity': 78,
     u'avewind': {u'degrees': 190, u'dir': u'S', u'kph': 21, u'mph': 13},
     u'conditions': u'Chance of a Thunderstorm',
     u'date': {u'ampm': u'PM',
      u'day': 26,
      u'epoch': u'1451178000',
      u'hour': 19,
      u'isdst': u'0',
      u'min': u'00',
      u'month': 12,
      u'monthname': u'December',
      u'monthname_short': u'Dec',
      u'pretty': u'7:00 PM CST on December 26, 2015',
      u'sec': 0,
      u'tz_long': u'America/Chicago',
      u'tz_short': u'CST',
      u'weekday': u'Saturday',
      u'weekday_short': u'Sat',
      u'yday': 359,
      u'year': 2015},
     u'high': {u'celsius': u'23', u'fahrenheit': u'74'},
     u'icon': u'chancetstorms',
     u'icon_url': u'http://icons.wxug.com/i/c/k/chancetstorms.gif',
     u'low': {u'celsius': u'18', u'fahrenheit': u'65'},
     u'maxhumidity': 0,
     u'maxwind': {u'degrees': 190, u'dir': u'S', u'kph': 32, u'mph': 20},
     u'minhumidity': 0,
     u'period': 3,
     u'pop': 80,
     u'qpf_allday': {u'in': 0.23, u'mm': 6},
     u'qpf_day': {u'in': 0.18, u'mm': 5},
     u'qpf_night': {u'in': 0.05, u'mm': 1},
     u'skyicon': u'',
     u'snow_allday': {u'cm': 0.0, u'in': 0.0},
     u'snow_day': {u'cm': 0.0, u'in': 0.0},
     u'snow_night': {u'cm': 0.0, u'in': 0.0}},
    {u'avehumidity': 82,
     u'avewind': {u'degrees': 254, u'dir': u'WSW', u'kph': 16, u'mph': 10},
     u'conditions': u'Thunderstorm',
     u'date': {u'ampm': u'PM',
      u'day': 27,
      u'epoch': u'1451264400',
      u'hour': 19,
      u'isdst': u'0',
      u'min': u'00',
      u'month': 12,
      u'monthname': u'December',
      u'monthname_short': u'Dec',
      u'pretty': u'7:00 PM CST on December 27, 2015',
      u'sec': 0,
      u'tz_long': u'America/Chicago',
      u'tz_short': u'CST',
      u'weekday': u'Sunday',
      u'weekday_short': u'Sun',
      u'yday': 360,
      u'year': 2015},
     u'high': {u'celsius': u'21', u'fahrenheit': u'69'},
     u'icon': u'tstorms',
     u'icon_url': u'http://icons.wxug.com/i/c/k/tstorms.gif',
     u'low': {u'celsius': u'9', u'fahrenheit': u'48'},
     u'maxhumidity': 0,
     u'maxwind': {u'degrees': 254, u'dir': u'WSW', u'kph': 24, u'mph': 15},
     u'minhumidity': 0,
     u'period': 4,
     u'pop': 100,
     u'qpf_allday': {u'in': 0.62, u'mm': 16},
     u'qpf_day': {u'in': 0.35, u'mm': 9},
     u'qpf_night': {u'in': 0.27, u'mm': 7},
     u'skyicon': u'',
     u'snow_allday': {u'cm': 0.0, u'in': 0.0},
     u'snow_day': {u'cm': 0.0, u'in': 0.0},
     u'snow_night': {u'cm': 0.0, u'in': 0.0}}]},
  u'txt_forecast': {u'date': u'1:17 AM CST',
   u'forecastday': [{u'fcttext': u'Sunny skies. High 71F. Winds SSE at 5 to 10 mph.',
     u'fcttext_metric': u'Sunny skies. High 22C. Winds SSE at 10 to 15 km/h.',
     u'icon': u'clear',
     u'icon_url': u'http://icons.wxug.com/i/c/k/clear.gif',
     u'period': 0,
     u'pop': u'0',
     u'title': u'Thursday'},
    {u'fcttext': u'Clear skies early will give way to occasional showers later during the night. Low 59F. Winds light and variable. Chance of rain 50%.',
     u'fcttext_metric': u'Clear in the evening then increasing clouds with showers after midnight. Low near 15C. Winds light and variable. Chance of rain 50%.',
     u'icon': u'nt_chancerain',
     u'icon_url': u'http://icons.wxug.com/i/c/k/nt_chancerain.gif',
     u'period': 1,
     u'pop': u'50',
     u'title': u'Thursday Night'},
    {u'fcttext': u'Cloudy with periods of rain. Thunder possible. High 67F. Winds SSE at 5 to 10 mph. Chance of rain 90%. Rainfall may reach one inch.',
     u'fcttext_metric': u'Cloudy with periods of rain. Thunder possible. High 19C. Winds SSE at 10 to 15 km/h. Chance of rain 90%. Rainfall may reach 25mm.',
     u'icon': u'rain',
     u'icon_url': u'http://icons.wxug.com/i/c/k/rain.gif',
     u'period': 2,
     u'pop': u'90',
     u'title': u'Friday'},
    {u'fcttext': u'Thunderstorms likely. Low 64F. Winds S at 5 to 10 mph. Chance of rain 90%.',
     u'fcttext_metric': u'Thunderstorms likely. Low 18C. Winds S at 10 to 15 km/h. Chance of rain 90%.',
     u'icon': u'nt_tstorms',
     u'icon_url': u'http://icons.wxug.com/i/c/k/nt_tstorms.gif',
     u'period': 3,
     u'pop': u'90',
     u'title': u'Friday Night'},
    {u'fcttext': u'Thunderstorms in the morning, then cloudy skies late. Record high temperatures expected. High 74F. Winds S at 10 to 20 mph. Chance of rain 80%.',
     u'fcttext_metric': u'Thunderstorms in the morning will give way to cloudy skies late. Record high temperatures expected. High 24C. Winds S at 15 to 30 km/h. Chance of rain 80%.',
     u'icon': u'chancetstorms',
     u'icon_url': u'http://icons.wxug.com/i/c/k/chancetstorms.gif',
     u'period': 4,
     u'pop': u'80',
     u'title': u'Saturday'},
    {u'fcttext': u'Scattered thunderstorms developing overnight. Low near 65F. Winds S at 10 to 15 mph. Chance of rain 40%.',
     u'fcttext_metric': u'Cloudy skies early. Scattered thunderstorms developing later at night. Low 18C. Winds S at 10 to 15 km/h. Chance of rain 40%.',
     u'icon': u'nt_tstorms',
     u'icon_url': u'http://icons.wxug.com/i/c/k/nt_tstorms.gif',
     u'period': 5,
     u'pop': u'40',
     u'title': u'Saturday Night'},
    {u'fcttext': u'Thunderstorms in the morning will give way to steady rain in the afternoon. Morning high of 69F with temps falling to near 55. SSW winds shifting to NNW at 10 to 15 mph. Chance of rain 100%.',
     u'fcttext_metric': u'Thunderstorms in the morning will give way to steady rain in the afternoon. Morning high of 21C with temps falling to 13 to 15. SSW winds shifting to NNW at 15 to 25 km/h. Chance of rain 100%.',
     u'icon': u'tstorms',
     u'icon_url': u'http://icons.wxug.com/i/c/k/tstorms.gif',
     u'period': 6,
     u'pop': u'100',
     u'title': u'Sunday'},
    {u'fcttext': u'Rain likely. Low 48F. Winds NE at 5 to 10 mph. Chance of rain 70%. Rainfall around a quarter of an inch.',
     u'fcttext_metric': u'Rain likely. Low 9C. Winds NE at 10 to 15 km/h. Chance of rain 70%. Rainfall near 6mm.',
     u'icon': u'nt_rain',
     u'icon_url': u'http://icons.wxug.com/i/c/k/nt_rain.gif',
     u'period': 7,
     u'pop': u'70',
     u'title': u'Sunday Night'}]}},
 u'response': {u'features': {u'forecast': 1},
  u'termsofService': u'http://www.wunderground.com/weather/api/d/terms.html',
  u'version': u'0.1'}}

'''
