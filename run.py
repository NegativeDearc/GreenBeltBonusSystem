# -*- coding:utf-8 -*-


from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from views import app

http_server = HTTPServer(WSGIContainer(app))
http_server.listen(5010,address='0.0.0.0')
IOLoop.instance().start()