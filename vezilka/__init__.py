from __future__ import absolute_import, division

from .lib import RESTzeug
from .model import Database

def make_app(config=None, **kwargs):
    config = config or {}
    config.update(kwargs)
    config['db'] = Database(config['db_url'])
    application = RESTzeug(config)
    return application

