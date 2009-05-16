import couchdb
import markup

server = couchdb.Server('http://localhost:5984/') # from config
db = server['vezilka'] # from config

def get_doc(id):
    return db.get(id)

def create_page(doc):
    db.create(doc)

def update_page(doc):
    db[doc.id] = doc
        
def get_page(slug):
    rows = db.view('_design/pages/_view/by_slug', key = slug).rows
    if len(rows) > 0:
        id = rows[0].id
        return get_doc(id)
    else:
        return None

def get_all_pages():
    return db.view('pages/all')

def get_parsed_content(doc):
    engine = markup.get_engine(doc['content_type'])
    content, meta = engine(doc['content'])
    return content, meta
