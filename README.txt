=======
Везилка
=======

Ова е имплементација на Везилка wiki/blog. Првата верзија на Везилка беше класична Pylons + SQLAlchemy апликација. Оваа верзија веќе не користи готов web framework туку custom-изиран врз база на Werkzeug_. Исто така не користи класична SQL база туку CouchDB.

WSGI апликацијата зависи од: Python-2.6, Werkzeug, Genshi, CouchDB
(сега за сега), и евентуално во иднина од formencode, simplejson, Creoleparser....

spec:

- GET http://host/app/page_name - read page
- GET http://host/app/page_name|edit - show edit form
- POST http://host/app/page_name - update page, redirect back

- GET http://host/app/page_name|delete - show delete confirm form
- POST http://host/app/page_name|delete - delete page, redirect (to undo page?)

- GET http://host/app/nonexistent_page -> Redirect to nonexistent_page|edit

Special pages:

- rss/atom: GET http://host/app/page_name|atom ?
- json interface: GET/POST http://host/app/.json/xxx ?

View the TODO_

.. _TODO: TODO
.. _Werkzeug: http://werkzeug.pocoo.org/
