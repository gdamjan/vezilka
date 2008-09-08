import couchdb
import markup

server = couchdb.Server('http://localhost:5984/') # from config
db = server['vezilka'] # from config

def get_doc(id):
    try:
        return db[id]
    except couchdb.client.ResourceNotFound:
        return None

def create_page(doc):
    db.create(doc)

def update_page(doc):
    db[doc.id] = doc
        
def get_page(slug):
    rows = db.view('pages/by_slug')[slug].rows
    try:
        id = rows[0].id
        return db[id]
    except StopIteration:
        return None
    except couchdb.client.ResourceNotFound:
        return None

def get_all_pages():
    return db.view('pages/all')

def get_parsed_content(doc):
    engine = markup.get_engine(doc['content_type'])
    content, meta = engine(doc['content'])
    return content, meta
