#!/usr/bin/env python
from weberror.evalexception import EvalException 
# EvalException depends on paste, tempita, pygments


from vezilka import Vezilka


#from paste.urlmap import URLMap
#from webob import exc
#app = URLMap({})
#app['/'] = exc.HTTPSeeOther(location='/wiki')
#app['/wiki'] = Vezilka()

app = Vezilka()
app = EvalException(app)

from wsgiref.simple_server import make_server
httpd = make_server('', 8000, app)
print "Serving HTTP on port 8000..."

# Respond to requests until process is killed
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    pass
