#! /usr/bin/python

import sys
USAGE = """\
Usage: 
    %s file.json [file2.json] ...
""" % sys.argv[0]
if len(sys.argv) <= 1:
    print USAGE
    sys.exit(1)

import simplejson
import couchdb
db = couchdb.Server('http://localhost:5984/')['vezilka']
for fname in sys.argv[1:]:
    docs = simplejson.load(file(fname))
    for doc in docs:
        if doc.has_key('_id'):
            db[doc['_id']] = doc
        else:
            db.create(doc)
