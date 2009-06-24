# -*- coding: utf-8 -*-
"""
    webpylike
    ~~~~~~~~~

    This module is based on Werkzeugs web.py like dispatch example, but
    heavily modified for this application. Unfortunetally it's not 
    generally usefull.

    :copyright: (c) 2009 by the Werkzeug Team, see AUTHORS for more details.
    :license: BSD.
"""
from utils import Request
from werkzeug.exceptions import HTTPException, MethodNotAllowed
from werkzeug.routing import Map, Rule, RuleFactory

def expose(rule, **kw):
    def decorate(cls):
        if not hasattr(cls, '_exposed'):
            cls._exposed = []
        cls._exposed.append((rule, kw))
        return cls
    return decorate

class WebPyApp(object):
    """
    An interface to a web.py like application.  It works like the web.run
    function in web.py
    """
    BASIC_METHODS = ('POST', 'GET', 'HEAD', 'PUT', 'DELETE')

    def __init__(self, config=None, **extra_conf):
        self.config = config or {}
        self.config.update(extra_conf)
        self.url_map = Map(redirect_defaults=False)

    def __call__(self, environ, start_response):
        request = Request(environ, self.url_map)
        try:
            cls, values = request.adapter.match()
            view = cls()
            view.app = self
            try:
                handler = getattr(view, request.method)
            except AttributeError, e:
                valid_methods = [m for m in self.BASIC_METHODS if hasattr(view, m)]
                raise MethodNotAllowed(valid_methods=valid_methods)
            response = handler(request, **values)
        except HTTPException, e:
            response = e
        return response(environ, start_response)

    def publish(self, module):
        for item in  dir(module):
            cls = getattr(module, item)
            if not hasattr(cls, '_exposed'):
                continue
            for rule, kw in cls._exposed:
                if not isinstance(rule, RuleFactory):
                    rule = Rule(rule, **kw)
                rule.endpoint = cls
                self.url_map.add(rule)
            # monkey patch the class to support HEAD if needed
            if hasattr(cls, 'GET') and not hasattr(cls, 'HEAD'):
                setattr(cls, 'HEAD', getattr(cls, 'GET'))
        return self.url_map

