
import vezilka
config = {
    'couchdb.url': 'http://localhost:5984/vezilka',
    'beaker.session.type': 'cookie',
    'beaker.session.key': 'vezilka',
    'beaker.session.validate_key': 'somesecret',
}

application = vezilka.app_factory(config)
