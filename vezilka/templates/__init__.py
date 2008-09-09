from os import path

from genshi.template import TemplateLoader
import genshi

search_path = path.dirname(__file__)
loader = TemplateLoader([search_path], auto_reload=True, variable_lookup="lenient")

def render(name, **context):
    suffix = path.splitext(name)[1]
    func = RENDER_ENGINES[suffix]
    return func(name, **context)

def render_genshi(name, **context):
    tmpl = loader.load(name)
    stream = tmpl.generate(HTML=genshi.HTML, **context)
    return stream.render('html', doctype='html', encoding=None) # string
    return stream.serialize('html', doctype='html') # generator

RENDER_ENGINES = {
 '.html': render_genshi,
# '.txt': render_txt,
# '.xml': render_xml,
# '.mak': render_mako,
}

