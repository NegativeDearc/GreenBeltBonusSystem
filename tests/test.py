# -*- coding:utf-8 -*-
__author__ = 'SXChen'

from flask import current_app

import os
import sys

# 直接从app导入create_app失败
path = os.path.abspath(os.path.dirname(__file__).join(os.path.pardir))
sys.path.append(path)

from app import create_app
from app import config

class test(object):
    def __init__(self):
        self.app = create_app(config['development'])
        self.app_context = self.app.app_context()

if __name__ == '__main__':
    t = test()
    print t.app
    print t.app_context