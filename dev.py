#!/usr/bin/env python
from paste.urlmap import URLMap
from weberror.evalexception import EvalException
from webob import exc

from vezilka import Vezilka


app = URLMap({})
app['/'] = exc.HTTPSeeOther(location='/wiki')
app['/wiki'] = Vezilka()

app = EvalException(app)
from paste import httpserver
httpserver.serve(app)
