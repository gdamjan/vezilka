# -*- coding: utf8 -*-
from __future__ import absolute_import, division
import urllib, time

from .model import get_page, get_parsed_content, markup, create_page, update_page
from .lib import *
from . import application


@application.expose("/", redirect_to='First_post')
@application.expose("/<path:pagename>")
class Page(object):

    def GET(self, req, pagename=u'First_post'):
        doc = get_page(pagename)
        if doc is None:
            raise NotFound()
        ctype = doc['content_type']
        if ctype.startswith('inline-text/'):
            c = Context()
            c.url = req.url_for(Page, pagename=pagename)
            c.edit_url = req.url_for(Edit, pagename=pagename)
            c.delete_url = req.url_for(Delete, pagename=pagename)
            c.pagename = pagename
            c.content, c.meta = get_parsed_content(doc)
            c.content_type = ctype
            c.created = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(doc['creation_time']))
            c.tags = doc['tags']
            return TemplatedResponse('show.html', c=c)
        elif ctype.startswith('text/'):
            return Response(doc['content'], mimetype=ctype)
        else:
            return Response(doc['content'], content_type=ctype, direct_passthrough=True)

@application.expose("/<path:pagename>|edit")
class Edit(object):

    def GET(self, req, pagename):
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
        c.url = req.url_for(Page, pagename=pagename)
        c.post_url = req.url_for(Edit, pagename=pagename)
        return TemplatedResponse('edit.html', c=c)

    def POST(self, req, pagename):
        doc = get_page(pagename)
        if doc is None:
            doc = {}
            doc['Type'] = 'page'
            doc['slug'] = pagename
            doc['creation_time'] = time.time()
            create_page(doc)
        doc = get_page(pagename)
        doc['tags'] = [ x.strip() for x in req.form.get('tags', '').split(',') ]
        doc['content'] = req.form['content']
        doc['content_type'] = req.form['content_type']
        update_page(doc)
        message = 'Successfully saved'
        url = req.url_for(Page, pagename=pagename)
        return redirect(url)

@application.expose("/<path:pagename>|delete")
class Delete(object):

    def GET(self, req, pagename):
        c = Context()
        c.pagename = pagename
        c.url = req.url_for(Delete, pagename=pagename)
        return TemplatedResponse('delete.html', c=c)

    def POST(self, req, pagename):
        # do the delete? ...
        url = req.url_for(Page, pagename=pagename)
        return redirect(url) 


@application.expose("/<path:pagename>|login")
class LoginController(object):

    def GET(self, req, pagename, username=None, status=None):
        c = Context()
        c.pagename = pagename
        c.username = username
        c.status = status
        c.url = self.request.relative_url(pagename, True)
        if self.is_logged():
            c.status = 'Already logged in!'
        return render('login.html', c=c)

    def POST(self, req, pagename):
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

    def get_logout(self, req, pagename):
        session = req.environ['beaker.session']
        session['admin'] = 0
        session.save()
        url = self.request.relative_url(pagename, True)
        raise exc.HTTPSeeOther(location=url.encode('utf-8'))

    def is_logged(self):
        session = self.request.environ['beaker.session']
        return session.get('admin') == 1
