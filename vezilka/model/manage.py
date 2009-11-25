# -*- encoding: utf8 -*-
from couchdb.design import ViewDefinition
import couchdb

from os import path
from datetime import datetime
import urlparse

views = [
    ViewDefinition('pages', 'by_date', 
        '''function(doc) { 
                if (doc.doc_type == 'page')  
                    emit(doc.creation_time, null) 
            }'''),
    ViewDefinition('pages', 'all', 
        '''function(doc) { 
                if (doc.doc_type == 'page') 
                    emit(doc._id, null) 
            }'''),
    ViewDefinition('pages', 'by_slug', 
        '''function(doc) { 
                if (doc.doc_type == 'page')  
                    emit(doc.slug, null)
            }'''),
    ViewDefinition('pages', 'by_type', 
        '''function(doc) { 
                if (doc.doc_type == 'page')  
                    emit(doc.content_type, null) 
            }'''),
    ViewDefinition('comments', 'by_date', 
        '''function(doc) { 
                if (doc.doc_type == 'comment')  
                    emit(doc.creation_time, null) 
            }'''),
    ViewDefinition('comments', 'all', 
        '''function(doc) { 
                if (doc.doc_type == 'comment')  
                    emit(null, null) 
            }'''),
    ViewDefinition('comments', 'by_parent', 
        '''function(doc) { 
                if (doc.doc_type == 'comment')  
                    emit(doc.parent, null) 
            }'''),
    ViewDefinition('tags', 'all', 
        '''function(doc) { 
                for(var i=0; i<doc.tags.length; i++) { 
                    emit(doc.tags[i], null) 
                } 
            }'''),
    ViewDefinition('tags', 'weight', 
        '''function(doc) { 
                for(var i=0; i<doc.tags.length; i++) { 
                    emit(doc.tags[i], null) 
                } 
            }''', 
        '''function(keys, values, combine) { 
                if (combine) { 
                    return sum(values); 
                } else { 
                    return values.length; 
                } 
            }''')
]

def readdocfile(name):
    pathname = path.join(path.dirname(__file__), '..', '..', name)
    fp = open(pathname)
    return fp.read().decode('utf-8')

docs = [
    {
        'slug': 'First_post',
        'doc_type': 'page',
        'content_type': 'inline-text/x-rst',
        'tags': [u'везилка', 'test', u'тест', u'кирилица'],
        'created': datetime.now().isoformat(),
        'modified': datetime.now().isoformat(),
        'content': readdocfile('README.txt'),
    },
    {
        'slug': 'TODO',
        'doc_type': 'page',
        'content_type': 'inline-text/x-rst',
        'tags': [u'везилка', 'test', u'тест', u'кирилица'],
        'created': datetime.now().isoformat(),
        'modified': datetime.now().isoformat(),
        'content': readdocfile('TODO.txt'),
    },
     
]

def initdb(db_url):
    scheme, netloc, path, params, query, fragment = urlparse.urlparse(db_url)
    hostname = urlparse.urlunparse((scheme, netloc, '/', '', '', ''))
    dbname = path[1:]
    try:
        server = couchdb.Server(hostname)
        db = server[dbname]
    except couchdb.client.ResourceNotFound:
        server = couchdb.Server(hostname)
        db = server.create(dbname)
    for v in views:
        v.sync(db)
    for d in docs:
        db.create(d)
