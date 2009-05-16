from __future__ import absolute_import, division

from .lib import WebPyApp

def make_app(config=None, **kwargs):
    config = config or {}
    config.update(kwargs)
    app = WebPyApp(config)
    return app

