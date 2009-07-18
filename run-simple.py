#!/usr/bin/env python
from os import path


import vezilka
app = vezilka.make_app(db_url="http://localhost:5984/vezilka")



if __name__ == '__main__':
    from werkzeug import run_simple, SharedDataMiddleware
    STATIC_PATH = path.join(path.dirname(__file__), "static")

    app = SharedDataMiddleware(app, {'/static':  STATIC_PATH})
    run_simple('', 5000, app, use_debugger=True, use_reloader=True)
