from __future__ import absolute_import, division
from beaker.middleware import SessionMiddleware
from .controller import Vezilka

class WSGI_app(object):
    def __init__(self, config):
        # do all time consuming initialization here
        self.config = config

    def __call__(self, environ, start_response):
        # make a clean object for each request
        app = Vezilka(self.config)
        return app(environ, start_response)

# PasteDeploy [paste.app_factory]
def app_factory(global_config, **local_conf):
    global_config.update(local_conf)
    app = WSGI_app(global_config)
    app = SessionMiddleware(app, global_config)
    return app

