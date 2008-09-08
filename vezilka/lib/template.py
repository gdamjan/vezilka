# example taken from the Genshi tutorial
# render() should be a method of the controler class so that it can work
# so this is an example only, it doesn't work as such

from os import path

from genshi.core import Stream
from genshi.output import encode, get_serializer
from genshi.template import Context, TemplateLoader

loader = TemplateLoader(
    path.join(path.dirname(__file__), '..', 'templates'),
    auto_reload=True
)

def output(filename, method='html', encoding='utf-8', **options):
    """Decorator for exposed methods to specify what template they should use
    for rendering, and which serialization method and options should be
    applied.
    """
    def decorate(func):
        def wrapper(self, *args, **kwargs):
            self._template = loader.load(filename)
            opt = options.copy()
            if method == 'html':
                opt.setdefault('doctype', 'html')
            serializer = get_serializer(method, **opt)
            stream = func(*args, **kwargs)
            if not isinstance(stream, Stream):
                return stream
            return encode(serializer(stream), method=serializer,
                          encoding=encoding)
        return wrapper
    return decorate

def render(self, **kwargs):
    """Function to render the given data to the template specified via the
    ``@output`` decorator.
    """
    template = self._template
    ctxt = Context()
    ctxt.push(kwargs)
    return template.generate(ctxt)
