from __future__ import absolute_import, division

# Bring them all in a single namespace
from werkzeug import redirect

from .utils import Request, Response, TemplatedResponse
from .webpylike import WebPyApp

class Context(object):
    pass
