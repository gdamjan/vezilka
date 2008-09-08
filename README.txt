Ова е имплементација на Везилка wiki/blog-от без Pylons.
WSGI апликацијата зависи само од Python-2.5, WebOb и Genshi
(сега за сега), и евентуално во иднина од formencode, simplejson,
Beaker и Paste.

spec:

GET http://host/app/page_name - read page
GET http://host/app/page_name|edit - show edit form
POST http://host/app/page_name - update page, redirect

GET http://host/app/page_name|delete - show delete confirm form
POST http://host/app/page_name|delete - delete page, redirect (to undo page?)

GET http://host/app/nonexistent_page -> Redirect to nonexistent_page|edit

Special pages:
rss/atom: GET http://host/app/page_name|atom ?
json interface: GET/POST http://host/app/.json/xxx ?

