#!/usr/bin/env python

## These two lines are needed to run on EL6
__requires__ = ['SQLAlchemy >= 0.8', 'jinja2 >= 2.4']
import pkg_resources

import sys
from werkzeug.contrib.profiler import ProfilerMiddleware

from downstreaming import APP
APP.debug = True

if '--profile' in sys.argv:
    APP.config['PROFILE'] = True
    APP.wsgi_app = ProfilerMiddleware(APP.wsgi_app, restrictions=[30])

if '--public' in sys.argv:
    listening_interface = '0.0.0.0'
else:
    listening_interface = '127.0.0.1'

APP.run(host=listening_interface)
