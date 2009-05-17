# make sure the /static urls is accessible via Apache

import vezilka
application = vezilka.make_app(db_url='http://localhost:5984/vezilka')
