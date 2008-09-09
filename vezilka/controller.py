# -*- coding: utf8 -*-
from __future__ import absolute_import, division
import urllib, time

from webob import exc

from .templates import render
from .lib import BaseWSGIDispatcher, Context
from .model import get_page, get_parsed_content, markup, create_page, update_page

class Vezilka(BaseWSGIDispatcher):
    def get_default(self, pagename):
        if not pagename:
            pagename = u'First_post' # default page, like index.html
        doc = get_page(pagename)
        if doc is None:
            raise exc.HTTPNotFound()
        ctype = doc['content_type']
        if ctype.startswith('inline-text/'):
            c = Context()
            c.url = self.request.relative_url(pagename, True)
            c.pagename = pagename
            c.content, c.meta = get_parsed_content(doc)
            c.content_type = doc['content_type']
            c.created = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(doc['creation_time']))
            c.tags = doc['tags']
            return render('page.html', c=c)
        elif ctype.startswith('text/'):
            body = doc['content'].encode('utf8')
            self.response.headers['Content-Type'] = ctype
            self.response.headers['Content-Length'] = len(body)
            self.response.body = body
            return None
        else:
            # think about binary stuff
            return None

    def get_edit(self, pagename):
        # FIXME: get config.default_markup?
        c = Context()
        c.content_type = u'inline-text/x-rst'
        c.pagename = pagename
        doc = get_page(pagename)
        if doc is not None:
            c.content = doc['content']
            c.content_type = doc['content_type']
            c.tags = ', '.join(doc['tags'])
        c.supported_content_types = markup.get_engine_list()
        c.url = self.request.relative_url(pagename, True)
        return render('edit.html', c=c)

    def post_default(self, pagename):
        req = self.request
        doc = get_page(pagename)
        if doc is None:
            doc = {}
            doc['slug'] = pagename
            doc['doc_type'] = 'page'
            doc['creation_time'] = time.time()
            create_page(doc)
        doc = get_page(pagename)
        doc['tags'] = [ x.strip() for x in req.params['tags'].split(',') ]
        doc['content'] = req.params['content']
        doc['content_type'] = req.params['content_type']
        update_page(doc)
        self.message = 'Successfully saved'
        url = urllib.quote(pagename.encode('utf8')) # FIXME, should be part of WebOb API
        url = req.relative_url(url, True)
        raise exc.HTTPSeeOther(location=url)

    def get_delete(self, pagename):
        c = Context()
        c.pagename = pagename
        c.url = self.request.relative_url(pagename, True)
        return render('delete.html', c=c)

    def post_delete(self, pagename):
        # do the delete? ...
        url = self.request.relative_url(pagename, True)
        raise exc.HTTPSeeOther(location=url.encode('utf-8')) # FIXME

    def get_atom(self, pagename):
        self.response.content_type = 'application/atom+xml'
        return u'<xml>'

    def get_login(self, pagename, username=None, status=None):
        c = Context()
        c.pagename = pagename
        c.username = username
        c.status = status
        c.url = self.request.relative_url(pagename, True)
        if self.is_logged():
            c.status = 'Already logged in!'
        return render('login.html', c=c)

    def post_login(self, pagename):
        req = self.request
        username = req.params['username']
        password = req.params['password']
        if (username, password) == ('admin', 'password'):
            session = self.request.environ['beaker.session']
            session['admin'] = 1
            session.save()
            url = self.request.relative_url(pagename, True)
            raise exc.HTTPSeeOther(location=url.encode('utf-8'))
        else:
            return self.get_login(pagename, username, 'Wrong username or password')

    def get_logout(self, pagename):
        session = self.request.environ['beaker.session']
        session['admin'] = 0
        session.save()
        url = self.request.relative_url(pagename, True)
        raise exc.HTTPSeeOther(location=url.encode('utf-8'))

    def is_logged(self):
        session = self.request.environ['beaker.session']
        return session.get('admin') == 1
