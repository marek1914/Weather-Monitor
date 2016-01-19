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




