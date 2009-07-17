# -*- coding: utf-8 -*-
"""
    restzeug
    ~~~~~~~~~

    A RESTful mini WSGI framework based on Werkzeug. It's based on the 
    webpylike dispatch example in Werkzeug, but has been heavily modified
    for this application. So, now it becomes generally usefull.

    To use this module, a knowledge of Werkzeug (http://werkzeug.pocoo.org/)
    is needed.
    
    :copyright: (c) 2009 Damjan Georgievski
    :copyright: (c) 2009 by the Werkzeug Team, see AUTHORS for more details.
    :license: BSD.
"""
from werkzeug import BaseRequest, BaseResponse
from werkzeug.exceptions import HTTPException, MethodNotAllowed, NotFound
from werkzeug.routing import Map, Rule, RuleFactory


def expose(rule, **kw):
    def decorate(cls):
        if not hasattr(cls, '_exposed'):
            cls._exposed = []
        cls._exposed.append((rule, kw))
        return cls
    return decorate


class Request(BaseRequest):
    """Encapsulates a request."""

    def __init__(self, environ, url_map, **kwargs):
        super(Request, self).__init__(environ, **kwargs)
        self.adapter = url_map.bind_to_environ(environ)

    def url_for(self, endpoint, _external=False, **values):
        return self.adapter.build(endpoint, values, force_external=_external)


class Response(BaseResponse):
    """Encapsulates a response."""
    default_mimetype = "text/html"


class RESTzeug(object):
    """
    Main WSGI application object for RESTzeug. 
    """
    __slots__ = ('config', 'url_map', 'REQUEST')
    HTTP_METHODS = ('HEAD', 'GET', 'POST', 'PUT', 'DELETE', 'TRACE', 'OPTIONS', 'CONNECT')

    def __init__(self, request_cls=None, config=None):
        self.config = config or {}
        self.REQUEST = request_cls or Request
        self.url_map = Map(redirect_defaults=False)

    def __call__(self, environ, start_response):
        request = self.REQUEST(environ, self.url_map)
        try:
            cls, values = request.adapter.match() # raises NotFound
            view = cls()
            if (request.method not in self.HTTP_METHODS) or \
                                not hasattr(view, request.method):
                valid_methods = [m for m in self.HTTP_METHODS if hasattr(view, m)]
                raise MethodNotAllowed(valid_methods=valid_methods)
            view.app = self
            handler = getattr(view, request.method)
            response = handler(request, **values)
        except (HTTPException, BaseResponse) as e:
            response = e
        return response(environ, start_response)

    def publish(self, *modules):
        '''Publish exposed classes in the modules provided as arguments'''
        for module in modules:
            self.publish_module(module)

    def publish_module(self, module):
        for cls_name in  dir(module):
            cls = getattr(module, cls_name)
            if not hasattr(cls, '_exposed'):
                # not an exposed class, skip
                continue
            for rule, kw in cls._exposed:
                if not isinstance(rule, RuleFactory):
                    rule = Rule(rule, **kw)
                rule.endpoint = cls
                self.url_map.add(rule)
            # monkey patch the class to support HEAD if needed
            if hasattr(cls, 'GET') and not hasattr(cls, 'HEAD'):
                setattr(cls, 'HEAD', getattr(cls, 'GET'))



