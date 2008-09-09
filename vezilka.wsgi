
from vezilka import app
config = {
    'couchdb.url': 'http://localhost:5984/vezilka',
    'beaker.session.type': 'cookie',
    'beaker.session.key': 'vezilka',
    'beaker.session.secret': 'somesecret',
}

application = app.app_factory(config)
