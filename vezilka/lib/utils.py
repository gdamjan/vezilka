from genshi.output import DocType
from genshi.template import TemplateLoader
from genshi import HTML

from werkzeug import BaseRequest, BaseResponse

from os import path
TEMPLATES_DIR = path.join(path.dirname(__file__), '..', 'templates')

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

class TemplatedResponse(Response):
    """Response class with built in template renderer."""

    loader = None
    
    def __init__(self, template, **data):
        if TemplatedResponse.loader is None:
            TemplatedResponse.loader = TemplateLoader(TEMPLATES_DIR, 
                            auto_reload=True, variable_lookup="lenient")
        self.template = self.loader.load(template) 
        self.stream = self.template.generate(HTML=HTML, **data)
        response = self.stream.render('xhtml', doctype=DocType.XHTML_STRICT)
        Response.__init__(self, response)

class Templated404(TemplatedResponse):
    default_status = 404



__all__ = ('Request', 'Response', 'TemplatedResponse', 'Templated404')
