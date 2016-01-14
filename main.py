#!/usr/bin/env python
"""
Ref - http://charlesleifer.com/blog/structuring-flask-apps-a-how-to-for-those-coming-from-django/

this is the "secret sauce" -- a single entry-point that resolves the
import dependencies.  If you're using blueprints, you can import your
blueprints here too.

then when you want to run your app, you point to main.py or `main.app`
"""
import os
os.environ["RUNTIME_CONFIG"] = 'dev'

from app import app, create_tables

from models import *
from views import *


if __name__ == '__main__':
    create_tables(db)
    app.run()

