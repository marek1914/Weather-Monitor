#!/usr/bin/env python

"""
An alternative means of getting a testing config can be seen here - http://stackoverflow.com/questions/15982801/custom-sqlite-database-for-unit-tests-for-code-using-peewee-orm

"""
import os
os.environ["RUNTIME_CONFIG"] = 'test'

import arrow #http://crsmithdev.com/arrow/

import unittest
from settings import TestingConfig

from flaskapp import app, create_tables

from models import *
from fetchData import *


class TestAll(unittest.TestCase):
    def setUp(self):
        create_tables(db)

    def tearDown(self):
        pass

    def assertInRange(self, val, minv, maxv, noneOkay = False, msg=None):
        if noneOkay and val == None:
            return
        self.assertLessEqual(val, maxv, msg)
        self.assertGreaterEqual(val, minv, msg)

    def create_test_data(self):
        pass

    def test_fetch_wunderground(self):
        assert fetchWundergroundData(CONDITIONS)
        assert fetchWundergroundData(ASTRONOMY)
        assert fetchWundergroundData(RECORDS)
        assert fetchWundergroundData(FORECAST)

    def testTimpstampConversion(self):
        from datetime import datetime
        res = fetchWundergroundData(CONDITIONS)
        res = res['current_observation'] # deferefence        
        dtstr = res['observation_time_rfc822']
        wgnow = convertWundergroundTimestamp(res['observation_time_rfc822'])
        now = datetime.utcnow()
        self.assertEqual(now.date(), wgnow.date())
        self.assertAlmostEqual(now.hour, wgnow.hour, delta=1)

    def test_load_current_conditions(self):
        cont = loadCurrentConditions()
        self.assertEqual(cont.period, 5)

    def test_fetch_wg_current_conditions(self):
        cond = loadCurrentConditions()
        # update with the current conditions from wunderground
        getWundergroundConditions(cond)
        self.assertInRange(cond.temperature, -50, 50)
        self.assertInRange(cond.dewpoint, -50, 50)
        self.assertInRange(cond.feel, -50, 50)
        self.assertInRange(cond.heatindex, -50, 50, True)
        self.assertInRange(cond.pressure, 900, 1100)
        self.assertInRange(cond.pressureTrend, -10, 10)
        self.assertInRange(cond.rainamt, 0, 250)
        self.assertInRange(cond.rainrate, 0, 100)
        self.assertInRange(cond.windchill, -50, 50)
        self.assertInRange(cond.windgust, 0, 150)
        self.assertInRange(cond.windspeed, 0, 150)
        self.assertInRange(cond.winddir, 0, 360)
        self.assertInRange(cond.uv, 0, 10)
        self.assertInRange(cond.solarradiation, 0, 1000, True)
 
    def test_save_current_conditions(self):
        cnt1 = Condition.select().count()
        cond = updateConditions() # save the newest conditions
        cond2 = loadCurrentConditions() # now reload them
        self.assertEqual(cond.__dict__, cond2.__dict__)
        cnt2 = Condition.select().count()
        self.assertEqual(cnt2, cnt1+1)
        data = Condition.select().get()
        for key,val in data._data.items():
            if key == 'when':
                #print "key:val (%s:%s) = %s" % (key, val, cond.when)
                t1 = arrow.get(val)
                t2 = arrow.get(cond.when)
                self.assertEqual(t1, t2)
            elif key in cond.__dict__:
                self.assertEqual(val, cond.__dict__[key])
                #print "key:val (%s:%s) = %s" % (key, val, cond.__dict__[key])
            else:
                pass 
                #print 'skipping key: %s' % key

    def test_save_new_conditions(self):
        "try saving the same conditions twice to the database, then change the time and save again"
        cnt1 = Condition.select().count()
        cond = updateConditions()
        cnt2 = Condition.select().count()
        self.assertEqual(cnt1, cnt2)  # same condition shouldn't produce a new record
        cond.when = arrow.utcnow().datetime
        updateConditions(cond)
        cnt3 = Condition.select().count()
        self.assertEqual(cnt2+1, cnt3) # changing the ts should probuce a new record

    def test_rainfall_simulated(self):
        cond = CurrentConditions()
        cond.setRain(24, 0)
        cond.setRain(24, 2)
        rate = cond.rainrate
        rate2 = cond.getRainRate()
        self.assertEqual(rate, rate2)



if __name__ == '__main__':
    unittest.main()