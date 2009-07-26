#!/usr/bin/env python
#
# Management script based on werkzeug.script
#
from werkzeug import script
from os import path

config = {
   'beaker.session.type': 'file',
   'beaker.session.cookie_expires': 300,
   'beaker.session.data_dir' : '/tmp',
   'template_dirs': path.join(path.dirname(__file__), 'vezilka', 'templates'),
   'static_dir': path.join(path.dirname(__file__), 'static'),
   'db_url': 'http://localhost:5984/vezilka',
   'admin' : 'http://softver.org.mk/damjan',
}


def make_app():
    import vezilka
    return vezilka.make_app(config)

def make_shell():
    from vezilka.model import Page
    application = make_app()
    database = config.get('CouchDB')

    return locals()

action_runserver = script.make_runserver(make_app,
        use_reloader=True, use_debugger=True)
action_shell = script.make_shell(make_shell)

if __name__ == '__main__':
    script.run()
