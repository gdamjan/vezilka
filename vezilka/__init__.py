from __future__ import absolute_import, division

from werkzeug import SharedDataMiddleware
from beaker.middleware import SessionMiddleware
from genshi.template import TemplateLoader

from .lib import RESTzeug
from .model import Database
from . import views

def make_app(config=None, full_stack=True, static_files=True, **kwargs):
    config = config or {}
    config.update(kwargs)
    config['CouchDB'] = Database(config['db_url'])
    config['GenshiLoader'] = TemplateLoader(config['template_dirs'],
            auto_reload=True, variable_lookup="lenient")
 
    application = RESTzeug(config=config)
    application.publish(views)

    if full_stack:
        application = SessionMiddleware(application, config)

    if static_files:
        application = SharedDataMiddleware(application, 
            {'/static': config['static_dir'] } )

    return application
