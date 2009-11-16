=======
Везилка
=======

Ова е имплементација на Везилка, wiki/blog системот, без Pylons.
WSGI апликацијата зависи само од Python-2.6, Werkzeug, CouchDB, Beaker и Genshi
(сега за сега), и евентуално во иднина од formencode, simplejson.


Стартање
========

Може да се тестира со стартање на вклучената скрипта „dev.py“, или ако е инсталиран PythonPaste со командата „paster serve --reload dev.ini“. Доколку користите mod_wsgi може да ја употребите скриптата vezilka.wsgi.



Спецификација
=============

| или ; е сепаратор за акција
. е сепаратор за формат, на пример .pdf генерира PDF, 
а би требало да се имплементира и: .atom, .rss, .txt и .json

GET http://host/app/page_name - покажи страна
GET http://host/app/page_name|edit - ја покажува формата за едитирање
POST http://host/app/page_name - ја снима промената, прави redirect на „покажи страна“

GET http://host/app/page_name|delete - покажува форма за потврда на бришење
POST http://host/app/page_name|delete - ја брише страната, покажува опција за undo

GET http://host/app/nonexistent_page - ако страната не постои редиректира на nonexistent_page|edit
