from __future__ import absolute_import, division

from .lib import RESTzeug
from .model import Database
from . import views

def make_app(config=None, **kwargs):
    config = config or {}
    config.update(kwargs)
    config['db'] = Database(config['db_url'])

    application = RESTzeug(config=config)
    application.publish(views)
    return application

