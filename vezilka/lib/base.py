import urllib
from webob import Request, Response, exc

class BaseWSGIDispatcher(object):
    """documentation"""
    ACTION_SEP = ';'
    DEFAULT_CHARSET = 'utf8'
    DEFAULT_ACTION = 'default'
    request = property(lambda self: self.__request, 
        doc = 'This is a WebOb Request object')
    response = property(lambda self: self.__response, 
        doc = 'This is a WebOb Response object')
    config = property(lambda self: self.__config,
        doc = 'This is a global app-level object')
 
    def __init__(self, config=None):
        """Read configuration, setup application"""
        self.__config = config

    def prepare(self, environ):
        req = Request(environ, charset=self.DEFAULT_CHARSET)
        resp = Response(charset=self.DEFAULT_CHARSET)
        self.__request = req
        self.__response = resp

        # req.path_info should be unicode, but it's not .. this is a bug in WebOb 0.9
        path_info = unicode(req.path_info, req.charset)
        path_info = path_info.lstrip('/')
        path_info, sep, action = path_info.partition(self.ACTION_SEP)
        if not action:
            action = self.DEFAULT_ACTION
        # since 'action' is used as a Python identifier (function name) it 
        # can't be non-ASCII. Python 3.0 will allow unicode identifiers.
        assert action == action.encode('ascii', 'ignore'), \
            '"action" can\'t be non-ASCII yet, ie before Python 3.0.'
        return path_info, action
    
    def dispatch(self, path_info, action):
        method_name = '%s_%s' % (self.request.method.lower(), action.lower())
        try:
            func = getattr(self, method_name)
        except AttributeError:
            raise exc.HTTPNotFound()
        return func(path_info)

    def render_result(self, result):
        # should be an unicode string
        # if None, assume "method" set self.response.body (or app_iter) itself
        if result is None:
            return self.response
        if isinstance(result, unicode):
            self.response.unicode_body = result
        if isinstance(result, str):
            self.response.body = result
        return self.response

    def __call__(self, environ, start_response):
        """WSGI entry point, dispatch to appropriate method"""
        try:
            path_info, action = self.prepare(environ)
            result = self.dispatch(path_info, action)
            resp = self.render_result(result)
            return resp(environ, start_response)
        except exc.HTTPException, e:
            return e(environ, start_response)
        except Exception, e:
            raise # debug
            return exc.HTTPInternalServerError()(environ, start_response)
    

    def url(self, *segments, **vars):
        base_url = self.request.application_url
        path = '/'.join(str(s) for s in segments) # FIXME str
        if not path.startswith('/'):
           path = '/' + path
        if vars:
            path += '?' + urllib.urlencode(vars) # FIXME unicode?
        return base_url + path
