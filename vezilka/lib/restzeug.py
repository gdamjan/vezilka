# -*- coding: utf-8 -*-
"""
    restzeug
    ~~~~~~~~~

    A RESTful mini WSGI framework based on Werkzeug. It's based on the 
    webpylike dispatch example in Werkzeug, but has been heavily modified
    for this application. So, now it becomes generally usefull.

    To use this module, a knowledge of Werkzeug (http://werkzeug.pocoo.org/)
    is a requirement.
    
    :copyright: (c) 2009 Damjan Georgievski
    :copyright: (c) 2009 by the Werkzeug Team, see AUTHORS for more details.
    :license: BSD.
"""
from werkzeug import BaseRequest, BaseResponse, redirect, abort
from werkzeug.exceptions import HTTPException, MethodNotAllowed, NotFound
from werkzeug.routing import Map, Rule, RuleFactory


def expose(rule, **kw):
    def decorate(cls):
        rules = getattr(cls, '_exposed', [])
        rules.append((rule, kw))
        setattr(cls, '_exposed', rules)
        return cls
    return decorate


class Request(BaseRequest):
    """Encapsulates a request."""

    def __init__(self, environ, adapter, app, **kwargs):
        super(Request, self).__init__(environ, **kwargs)
        self.adapter = adapter
        self.app = app

    def url_for(self, endpoint, _external=False, **values):
        # if endpoint is not a string, the it must be in the url_map
        if not isinstance(endpoint, basestring):
            return self.adapter.build(endpoint, values, force_external=_external)
        # if endpoint is an absolute url (string)
        if endpoint.startswith('/'):
            if _external:
                return self.host_url + endpoint[1:]
            return endpoint
        # or else it's app-relative url:
        if _external:
            return self.url_root + endpoint
        return self.script_root + '/' + endpoint

    def redirect_to(self, endpoint, _code=301, **values):
        location = self.url_for(endpoint, _external=True, **values)
        return redirect(location, code=_code)


class Response(BaseResponse):
    """Encapsulates a response."""
    default_mimetype = "text/html"


class RESTzeug(object):
    """
    Main WSGI application object for RESTzeug. 
    """
    __slots__ = ('config', 'url_map', 'DEFAULT_REQUEST')
    HTTP_METHODS = ('HEAD', 'GET', 'POST', 'PUT', 'DELETE', 'TRACE', 'OPTIONS', 'CONNECT')

    def __init__(self, request_cls=None, config=None):
        self.DEFAULT_REQUEST = Request if request_cls is None else request_cls
        self.config = {} if config is None else config
        self.url_map = Map(redirect_defaults=False)

    def __call__(self, environ, start_response):
        adapter = self.url_map.bind_to_environ(environ)
        try:
            view_cls, values = adapter.match() # raises NotFound
            view = view_cls()
            request_cls = getattr(view, 'REQUEST', self.DEFAULT_REQUEST)
            req = request_cls(environ, adapter, self)
            if (req.method not in self.HTTP_METHODS) or \
                                not hasattr(view, req.method):
                valid_methods = [m for m in self.HTTP_METHODS if hasattr(view, m)]
                raise MethodNotAllowed(valid_methods=valid_methods)
            view.app = self
            handler = getattr(view, req.method)
            response = handler(req, **values)
        except HTTPException as exc:
            response = exc
        return response(environ, start_response)

    def publish(self, *modules):
        '''Publish exposed classes in the modules provided as arguments'''
        for module in modules:
            self.publish_module(module)

    def publish_module(self, module):
        for cls_name in  dir(module):
            cls = getattr(module, cls_name)
            rules = getattr(cls, '_exposed', None)
            # if not an exposed class, just skip it
            if rules is None:
                continue
            for rule, kw in rules:
                if not isinstance(rule, RuleFactory):
                    rule = Rule(rule, **kw)
                rule.endpoint = cls
                self.url_map.add(rule)
            # monkey patch the class to support HEAD if needed
            if hasattr(cls, 'GET') and not hasattr(cls, 'HEAD'):
                setattr(cls, 'HEAD', getattr(cls, 'GET'))



