# -*- coding:utf-8 -*-

from flask import Flask
from config import config

def create_app(conf):
    app = Flask(__name__)
    app.config.from_object(conf)
    return app

app = create_app(config['production'])

# debug 模式关闭时启用日志记录
# 尝试采用邮件发送
if not app.debug:
    from app.ext.log import DebugFalseLog
    handler = DebugFalseLog().get_handler()
    app.logger.addHandler(handler)

from app.views import views
