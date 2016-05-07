# -*- coding:utf-8 -*-
__author__ = 'SXChen'

import os
from sys import platform

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = 'JLGO8-81NLD-P1NXZ-M0128E-91JAM'
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True #消除警告,默认配置为None

    if platform.startswith('win'):
        DATABASE_PATH = basedir + '\\app\models\CTLSS_BONUS_DB'
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + basedir + '\\app\models\CTLSS_BONUS_DB'
    else:
        DATABASE_PATH = basedir + '/app/models/CTLSS_BONUS_DB'
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + basedir + '/app/models/CTLSS_BONUS_DB'

class DevelopmentConfig(Config):
    SQLALCHEMY_ECHO = True
    DEBUG = True


class ProductionConfig(Config):
    SQLALCHEMY_ECHO = False
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
