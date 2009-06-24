#!/usr/bin/env python
from os import path

from werkzeug import run_simple, SharedDataMiddleware

import vezilka
import vezilka.views

STATIC_PATH = path.join(path.dirname(__file__), "static")

app = vezilka.make_app(db_url="http://localhost:5984/vezilka")
app.publish(vezilka.views)

if __name__ == '__main__':
    app = SharedDataMiddleware(app, {'/static':  STATIC_PATH})
    run_simple('', 5000, app, use_debugger=True, use_reloader=True)
