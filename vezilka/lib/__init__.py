from __future__ import absolute_import, division

# Bring them all in a single namespace
from werkzeug import redirect

from .webpylike import WebPyApp, expose
from .utils import *

class Context(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
