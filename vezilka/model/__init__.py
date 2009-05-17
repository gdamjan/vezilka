from couchdb.schema import Document, DateTimeField, TextField, DictField, Schema
from couchdb.client import Database
import markup

from datetime import datetime

class Page(Document):
    slug = TextField()
    Type = TextField(default='page')
    content_type = TextField(default='inline-text/x-rst')
    datetime = DictField(Schema.build(
        created = DateTimeField(default=datetime.now),
        modified = DateTimeField(default=datetime.now)
    ))
    content = TextField()
 
    def store(self, db, **kwargs):
        self.datetime['modified'] = datetime.now()
        super(Page, self).store(db, **kwargs)

    @property 
    def meta(self):
        if not hasattr(self, '_meta'):
            self.get_parsed_content()
        return self._meta

    @property 
    def html(self):
        if not hasattr(self, '_body'):
            self.get_parsed_content()
        return self._body

    def get_parsed_content(self):
        engine = markup.get_engine(self['content_type'])
        self._body, self._meta = engine(self['content'])
        return self._body, self._meta



class Database(Database):
 
    def by_slug(self, slug):
        x = self.first('_design/pages/_view/by_slug', key=slug)
        if x is not None:
            return Page.load(self, x.id)
        else:
            return None

    def first(self, name, **options):
        v = self.view(name, **options)
        if len(v) > 0:
            return v.rows[0]
        else:
            return None

    @property
    def all_pages(self):
        return self.view('_design/pages/_view/all')

    @property
    def all_comments(self):
        return self.view('_design/comments/_view/all')


