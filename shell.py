#!/usr/bin/env python

import subprocess

from app import app, create_tables
from models import *

create_tables(db)

#subprocess.call("ipython")

from IPython import start_ipython
start_ipython(argv=[])