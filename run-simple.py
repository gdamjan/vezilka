#!/usr/bin/env python
from os import path

from werkzeug import run_simple, SharedDataMiddleware

from vezilka import application
import vezilka.views


STATIC_PATH = path.join(path.dirname(__file__), "static")
app = SharedDataMiddleware(application, {'/static':  STATIC_PATH})

if __name__ == '__main__':
    run_simple('', 5000, app, use_debugger=True, use_reloader=True)
