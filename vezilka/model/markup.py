# -*- coding: utf-8 -*-

__engines__ = {}

def get_engine_list():
    return sorted(__engines__.keys())

def get_engine(name, default=None):
    return __engines__.get(name, default)

def register_engine(name, engine):
    __engines__[name] = engine

# maybe an engine should be a class that supports two methods
# process and documentation?
def docutils_engine(content):
    from docutils.core import publish_parts
    meta = {}
    pp = publish_parts(content, writer_name="html")
    body = pp["html_body"]
    meta['title'] = pp['title']
    return body, meta

def textile_engine(content):
    import textile
    meta = {}
    body = textile.textile(content.encode('utf-8'), encoding='utf-8', output='utf-8')
    body = unicode(body, 'utf-8')
    body = u'<div class="document">%s</div>' % body
    return body, meta

def wrap_engine(content):
    meta = {}
    body = u'<div class="document">%s</div>' % content
    return body, meta

def aether_engine(content):
    import aether_markup
    meta = {}
    body = aether_markup.markup(content, meta, outermost=True)
    return body, meta

def null_engine(content):
    meta = {}
    return content, meta


# This could be also done if all the markup parsers/generators supported a
# common interface and supported a setuptools 'entrypoint'.
register_engine('inline-text/x-rst', docutils_engine)
register_engine('inline-text/x-textile', textile_engine)
register_engine('inline-text/x-aether', aether_engine)
register_engine('inline-text/html', wrap_engine)
register_engine('text/plain', null_engine)
register_engine('text/html', null_engine)


__all__ = [ 'register_engine', 'get_engine_list', 'get_engine' ]
