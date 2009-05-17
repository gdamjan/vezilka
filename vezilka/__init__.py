from __future__ import absolute_import, division

# application will be a global singleton instance. the consequence of it
# is that the applicaiton can't be used more than once in a single 
# interpreter. Maybe rethink this??


application = None

from .lib import WebPyApp
from .model import Database

def make_app(config=None, **kwargs):
    global application
    if application is not None:
        return application
    config = config or {}
    config.update(kwargs)
    config['db'] = Database(config['db_url'])
    application = WebPyApp(config)
    return application

