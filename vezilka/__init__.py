from __future__ import absolute_import, division

from werkzeug import SharedDataMiddleware
from beaker.middleware import SessionMiddleware
from genshi.template import TemplateLoader

from .lib import RESTzeug
from .model import Database
from . import views

def make_app(config=None, **kwargs):
    config = config or {}
    config.update(kwargs)
    config['CouchDB'] = Database(config['db_url'])
    config['GenshiLoader'] = TemplateLoader(config['template_dirs'],
            auto_reload=True, variable_lookup="lenient")
 
    application = RESTzeug(config=config)
    application.publish(views)
 
    if 'beaker.session.type' in config:
        application = SessionMiddleware(application, config)

    if 'static_dir' in config:
        application = SharedDataMiddleware(application, 
            {'/static': config.get('static_dir') } )

    return application
