import os


class Config(object):
    APP_ROOT = os.path.dirname(os.path.realpath(__file__))
    CONDITIONS_FILE = os.path.join(APP_ROOT, 'conditions.txt')
    FORECAST_FILE = os.path.join(APP_ROOT, 'forecast.txt')
    DATABASE = os.path.join(APP_ROOT, 'data.db')
    TIMEZONE = 'US/Central'
    UNITS_TEMP = 'F' # 'C'
    UNITS_DIST = 'in' # 'mm'
    UNITS_SPEED = 'knots' # kph, mph
    UNITS_PRESSURE = 'mb'
    
    WUG_KEY = 'f843bbca5bf0222c'
    WUG_ROOT = 'http://api.wunderground.com/api/'
    #LOCATION = 'KY/Mount_Hermon'
    LOCATION = 'pws:KKYMOUNT35' # our Ambient Weather station. Format: pws:PWS_ID
    
    
    DEBUG = False
    TESTING = False
    
    

class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    DATABASE = ':memory:'




