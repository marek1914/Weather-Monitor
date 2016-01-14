from peewee import *    # see - https://github.com/coleifer/peewee

import app

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

db = SqliteDatabase(app.config.DATABASE)

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


def CtoF(degC):
    return 32 + (1.8 * degC)


class CurrentConditions(object):
    """Dynamic store of the most recent conditions as retrieved from Wunderground and local sensors.
     It is not a model, but there is no better place to define it.
    """
    def __init__(self, period=5, metric=False): # mins
        self.period = period
        self.metric = metric
        self.rainamt_prev = 0
        self.rainamt = 0

    def getTemperatureInUnits(self, degC, metric=None):
        if metric == None: # python won't let us pass self.metric for a default??
            metric = self.metric
        return degC if metric else CtoF(degC)

    def setTimestamp(self, dt):
        self.when = dt

    def setTemperature(self, temp): # in degC
        self.temperature = temp
    def getTemperature(self):
        return self.getTemperatureInUnits(self.temperature)

    def setPressure(self, pressure): # millibars
        self.pressure = pressure
    def getPressure(self):
        pass #todo return in eng/metric
    def setPressureTrend(self, trend):
        self.pressureTrend = trend

    def setHumidity(self, humidity): # %
        self.humidity = humidity

    def setWind(self, deg, speed, gust):
        "degrees, kph, kph"
        self.winddir = deg
        self.windspeed = speed
        self.windgust = gust
    def getWindDirection(self):
        return self.winddir
    def getWindHeading(self):
        "Return compass dir"
        pass #todo

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
        pass # todo

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
                -0.00683783 * pow(temperature, 2) +
                -0.05481717 * pow(percentHumidity, 2) +
                0.00122874 * pow(temperature, 2) * percentHumidity +
                0.00085282 * temperature*pow(percentHumidity, 2) +
                -0.00000199 * pow(temperature, 2) * pow(percentHumidity, 2))

            # now apply some additional corrections
            if((percentHumidity < 13) and (temperature >= 80.0) and (temperature <= 112.0)):
                hi -= ((13.0 - percentHumidity) * 0.25) * sqrt((17.0 - abs(temperature - 95.0)) * 0.05882)
            elif((percentHumidity > 85.0) and (temperature >= 80.0) and (temperature <= 87.0)):
                hi += ((percentHumidity - 85.0) * 0.1) * ((87.0 - temperature) * 0.2);

        hi = FtoC(hi) # convert back to C
        return self.getTemperatureInUnits(hi)
        #return self.getTemperatureInUnits(self.heatindex) # calculate when we have our own data

    def setWindChill(self, wc):
        "This field can also be calculated"
        self.windchill = wc
    def getWindChill(self):
        return self.getTemperatureInUnits(self.windchill) # calculate when we have our own data

    def setRealFeel(self, feel):
        "This field can also be calculated"
        self.feel = feel
    def getRealFeel(self):
        return self.getTemperatureInUnits(self.feel) # calculate when we have our own data

    def setDewpoint(self, dp):
        "This field can also be calculated"
        self.dewpoint = dp
    def getDewpoint(self):
        return self.getTemperatureInUnits(self.dewpoint) # calculate when we have our own data

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
