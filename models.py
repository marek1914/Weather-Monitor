from math import log, sqrt
import arrow

from peewee import *    # see - https://github.com/coleifer/peewee

from flaskapp import app
from funcs import *

"""
Weather Sources:
* Wunderground -
* pollen - scrape from - http://www.wunderground.com/DisplayPollen.asp?Zipcode=42157
* icon # eg 'cloudy'; for url's to display, see - http://www.wunderground.com/weather/api/d/docs?d=resources/icon-sets

Measurement Notes:
* For solar radiation measurement, see - http://www.instesre.org/construction/pyranometer/pyranometer.htm
* heating/cooling day computation - http://www.wunderground.com/about/faq/degreedays.asp
* growing degree day computation - https://en.wikipedia.org/wiki/Growing_degree-day

Info not stored:
    heatindex = FloatField()
    windchill = FloatField()
    feel = FloatField()
    dewpoint = IntegerField() # celcius
    heatingday = BooleanField()
    coolingday = BooleanField()
    growdegreedays = FloatField()


For adding an admin page, see this article - http://charlesleifer.com/blog/integrating-flask-microframework-peewee-orm/

For dynamic database determination, see - https://github.com/coleifer/peewee/blob/master/docs/peewee/database.rst
"""

db = SqliteDatabase(app.config['DATABASE'])

class BaseModel(Model):
    "Define the database meta to simplify our models"
    class Meta:
        database = db

class Condition(BaseModel):
    "Current conditions, stored every 5 mins"
    when = DateTimeField()
    temperature = FloatField(null=True) # celcius
    pressure = IntegerField(null=True) # millibars
    humidity = IntegerField(null=True) # %
    winddir = IntegerField(null=True) # degrees
    windspeed = FloatField(null=True) # kph
    windgust = FloatField(null=True) # kph
    rainrate = IntegerField(null=True) # mm/hr (ave over interval)
    rainamt = IntegerField(null=True) # mm total over interval
    solarradiation = IntegerField(null=True) #w/m2
    leafmoisture = IntegerField(null=True)
    lightning = IntegerField(null=True)

class Environ(BaseModel):
    "environmental conditions on a daily basis"
    date = DateField()
    uv = IntegerField() # uv index, per - http://www.epa.gov/sunsafety/uv-index-scale-1
    visibility = FloatField() # km
    soilmoisture = IntegerField()
    soiltemp = FloatField() # celcius
    pollen = FloatField()
    moonage = IntegerField() # days
    moonlumin = IntegerField # % illuminated
    moonphase = CharField()
    moonrise = DateTimeField()
    moonset = DateTimeField()
    sunrise = DateTimeField()
    sunset = DateTimeField()


class Record(BaseModel):
    "daily records"
    date = DateField()
    tempmin = FloatField()
    tempmax = FloatField()
    windspeed = FloatField()
    rain = IntegerField()
    snow = IntegerField()
    solarradiation = IntegerField()
    leafmoisture = IntegerField()
    lightning = IntegerField()
    chillhrs = IntegerField()




class CurrentConditions(object):
    """Dynamic store of the most recent conditions as retrieved from Wunderground and local sensors.
     It is not a model, but there is no better place to define it.
    """
    def __init__(self, period=5, metric=False): # mins
        self.period = period
        self.metric = metric
        self.rainamt_prev = 0
        self.rainamt = 0


    def setTimestamp(self, dt):
        self.when = dt

    def setTemperature(self, temp): # in degC
        self.temperature = temp
    def getTemperature(self):
        return getTemperatureInUnits(self.temperature)

    def setPressure(self, pressure): # millibars
        self.pressure = pressure
        lastHours = arrow.utcnow().replace(hours=-4).datetime
        history = Condition.select().filter(Condition.when > lastHours)
        try: # will fail testing due to lack of historical data
            earlier = history.order_by(Condition.when.asc()).get()
            self.pressureTrend = pressure - earlier.pressure
        except:
            self.pressureTrend = 0

    def getPressure(self):
        pass #todo return in eng/metric
    # def setPressureTrend(self, trend):
    #     self.pressureTrend = trend

    def setHumidity(self, humidity): # %
        self.humidity = humidity

    def setWind(self, deg, speed, gust):
        "degrees, kph, kph"
        self.winddir = deg
        self.windspeed = speed
        self.windgust = gust
        lastHour = arrow.utcnow().replace(hours=-1).datetime
        history = Condition.select().filter(Condition.when > lastHour)
        dirs = [cond.winddir for cond in history]
        dirs.append(deg)
        mindir = min(dirs)
        maxdir = max(dirs)
        if not (deg >= mindir and deg <= maxdir): # swap them - we need to go the other way around the circle
            mindir, maxdir = maxdir, mindir
        self.winddir_min = mindir
        self.winddir_max = maxdir
    def getWindDirection(self):
        return self.winddir
    def getWindDirRange(self):
        return self.winddir_min, self.winddir_max
    def getWindHeading(self):
        "Return compass dir"
        pass #todo
    def getWindSpeed(self):
        return rint(getSpeedInUnits(self.windspeed))
    def getWindGust(self):
        return rint(getSpeedInUnits(self.windgust))

    def setRain(self, rate, amt):
        """
        Rate: mm/hr, Amt: mm (total over 24hrs)
        To get the amt over our interval, we will store the previously reported amount and use it and
        the new amount to get the interval amount.
        """
        self.rainrate = rate
        self.rainamt_prev = self.rainamt
        self.rainamt = amt
    def getRainPeriodAmt(self):
        "Amount over our interval period"
        return self.rainamt - self.rainamt_prev
    def getRainRate(self):
        return self.getRainPeriodAmt() * (60 / self.period)

    def setSolarRadiation(self, sr):
        self.solarradiation = sr

    #leafmoisture = IntegerField()
    #lightning = IntegerField()

    "------------These fields are not saved to the DB-------------------"
    def setIcon(self, icon):
        self.icon=icon
    def getIconUrl(self):
        ICON_SET = 'a'
        night = False # TODO - determine from sunrise/sunset data
        PREFIX = 'nt_' if night else ''
        return 'http://icons.wxug.com/i/c/{set}/{icon}.gif'.format(set=ICON_SET, icon=PREFIX + self.icon)

    def setOutlook(self, outlook):
        self.outlook = outlook

    def setHeatIndex(self, hi):
        """This field can also be calculated. See - http://www.wpc.ncep.noaa.gov/html/heatindex_equation.shtml
            Adafruit has already written the algorithm up. See -
        """
        self.heatindex = hi
    def getHeatIndex(self):
        """ Algorithm taken from https://github.com/adafruit/DHT-sensor-library/blob/master/DHT.cpp
            with the original at http://www.wpc.ncep.noaa.gov/html/heatindex_equation.shtml
        """
        # Using both Rothfusz and Steadman's equations
        # http://www.wpc.ncep.noaa.gov/html/heatindex_equation.shtml
        # temp is in C, we need F for the calculation
        temperature = CtoF(self.temperature)
        percentHumidity = self.humidity

        # first try the simple calc, which is best for hi < 80:
        hi = 0.5 * (temperature + 61.0 + ((temperature - 68.0) * 1.2) + (percentHumidity * 0.094));

        if (hi > 79):
            hi = (-42.379 +
                2.04901523 * temperature +
                10.14333127 * percentHumidity +
                -0.22475541 * temperature*percentHumidity +
                -0.00683783 * temperature*temperature +
                -0.05481717 * percentHumidity*percentHumidity +
                0.00122874 * temperature*percentHumidity * percentHumidity +
                0.00085282 * temperature*percentHumidity*percentHumidity +
                -0.00000199 * temperature*temperature * percentHumidity*percentHumidity)

            # now apply some additional corrections
            if((percentHumidity < 13) and (temperature >= 80.0) and (temperature <= 112.0)):
                hi -= ((13.0 - percentHumidity) * 0.25) * sqrt((17.0 - abs(temperature - 95.0)) * 0.05882)
            elif((percentHumidity > 85.0) and (temperature >= 80.0) and (temperature <= 87.0)):
                hi += ((percentHumidity - 85.0) * 0.1) * ((87.0 - temperature) * 0.2);

        hi = FtoC(hi) # convert back to C
        return rint(getTemperatureInUnits(hi))
        #return self.getTemperatureInUnits(self.heatindex) # calculate when we have our own data

    def setWindChill(self, wc):
        "This field can also be calculated"
        self.windchill = wc
    def getWindChill(self):
        return rint(getTemperatureInUnits(self.windchill)) # calculate when we have our own data

    def setRealFeel(self, feel):
        "This field can also be calculated"
        self.feel = feel
    def getRealFeel(self):
        return rint(getTemperatureInUnits(self.feel)) # calculate when we have our own data

    def setDewpoint(self, dp):
        "This field can also be calculated"
        self.dewpoint = dp
    def getDewpoint(self):
        #return rint(getTemperatureInUnits(self.dewpoint)) # calculate when we have our own data

        # from https://en.wikipedia.org/wiki/Dew_point
        T = self.temperature
        rh = self.humidity
        a = 6.1121
        b = 17.368 if T > 0 else 17.966
        c = 238.88 if T > 0 else 247.15
        gamma = log(rh/100.0) + ((b * T) / (c + T))
        dp = (c * gamma) / (b - gamma)
        return rint(getTemperatureInUnits(dp))

    # these are daily environ amts, but they come with the conditions call, so store them
    def setUV(self, uv):
        self.uv = uv

    def setVisibility(self, vs):
        self.visibility = vs

    def saveToDb(self):
        data = Condition(
            when=self.when,
            temperature=self.temperature,
            pressure=self.pressure,
            humidity=self.humidity,
            winddir=self.winddir,
            windspeed=self.windspeed,
            windgust=self.windgust,
            rainrate=self.rainrate,
            rainamt=self.getRainPeriodAmt(),
            solarradiation=self.solarradiation,
        )
        data.save()

LOW = 0
HIGH = 1

class ForecastTemp(object):
    def __init__(self, high, temp):
        self.high = high
        self.temp = temp
    def getLabel(self):
        return 'High' if self.high else 'Low'
    def getValue(self):
        return rint(getTemperatureInUnits(self.temp))

class DailyForecast(object):
    """Dynamic store of the forecast as retrieved from Wunderground.
     It is not a model, but there is no better place to define it.
    """
    def __init__(self): # mins
        pass

    def setTimestamp(self, ts):
        "set when using epoch ts"
        self.when = arrow.get(ts).datetime # utc

    def setLow(self, degC):
        "The low is for the following morning"
        self.low = degC

    def setHigh(self, degC):
        "The high is for the current day"
        self.high = degC

    def setWind(self, speed, dir):
        self.windspeed = speed
        self.winddir = dir

class Forecast(object):
    def __init__(self):
        self.daily = []
        self.hourly = []
        self.pastTemps = []
        self.futureTemps = []

    def setDaily(self, forecasts):
        self.daily = forecasts
        self.calcHiLows()

    def setHourly(self, forecasts):
        self.hourly = forecasts

    def calcHiLows(self):
        "Calculate past & future hi/lows"
        "NOTE: forecasts should be retrieved at 6am & 6pm daily"
        now = arrow.get().now() # local, not utc
        self.pastTemps = []
        self.futureTemps = []
        startHr = arrow.utcnow().replace(hours=-12).datetime
        history2nd12 = Condition.select().filter(Condition.when > startHr)
        startHr2 = arrow.utcnow().replace(hours=-24).datetime
        history1st12 = Condition.select().filter(Condition.when > startHr2).filter(Condition.when < startHr)

        "Figure the future hi & low"
        if now.hour > 17: # after 5pm
            # The afternoon high is past, so the morning's low should be 1st shown
            # today's low is actually tomorrows
            self.futureTemps.append(ForecastTemp(LOW, self.daily[0].low))
            # today's high is past now, so get tomorrow's high
            self.futureTemps.append(ForecastTemp(HIGH, self.daily[1].high))

            high = max([cond.temperature for cond in history2nd12])
            low = min([cond.temperature for cond in history1st12])
            self.pastTemps.append(ForecastTemp(LOW, low))
            self.pastTemps.append(ForecastTemp(HIGH, high))

        else: # now.hour is before 5, presumably sometime in the morning after the low
            # the morning low is past, the afternoon high is coming up
            self.futureTemps.append(ForecastTemp(HIGH, self.daily[0].high))
            self.futureTemps.append(ForecastTemp(LOW, self.daily[0].low))

            low = min([cond.temperature for cond in history2nd12])
            high = max([cond.temperature for cond in history1st12])
            self.pastTemps.append(ForecastTemp(HIGH, high))
            self.pastTemps.append(ForecastTemp(LOW, low))
