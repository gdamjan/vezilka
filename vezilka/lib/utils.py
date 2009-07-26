from __future__ import absolute_import, division

from genshi.output import DocType
from genshi.template import TemplateLoader

from .restzeug import Response, Request as BaseRequest

class Request(BaseRequest):
    '''This is the central Request class used in Vezilka. It will need to
    supply all the API needed by the views (controllers)'''

    def render(self, template_name, **data):
        loader = self.global_config['GenshiLoader']
        template = loader.load(template_name)
        stream = template.generate(req=self, **data)
        response = stream.render('html', doctype=DocType.HTML_TRANSITIONAL)
        # response = stream.render('xhtml', doctype=DocType.XHTML_STRICT)
        return Response(response)



__all__ = ('Request', )
