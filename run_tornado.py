# -*- coding:utf-8 -*-


from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from app import app

http_server = HTTPServer(WSGIContainer(app))
#http_server.listen(8888,address='0.0.0.0')
http_server.listen(8888)
IOLoop.instance().start()