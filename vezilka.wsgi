# make sure the /static urls is accessible via Apache

import vezilka
from os import path

config = {
   'beaker.session.type': 'file',
   'beaker.session.cookie_expires': 300,
   'beaker.session.data_dir' : '/tmp',
   'template_dirs': path.join(path.dirname(__file__), 'vezilka', 'templates'),
   'db_url': 'http://localhost:5984/vezilka',
   'admin' : 'http://softver.org.mk/damjan',
}

application = vezilka.make_app(config)
