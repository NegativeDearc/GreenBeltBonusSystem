__author__ = 'SXChen'

import os
from sys import platform

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'WELCOME TO SIX_SIGMA TEAM'
    if platform.startswith('win'):
        DATABASE_PATH = basedir + '\\app\models\CTLSS_BONUS_DB'
    else:
    	DATABASE_PATH = basedir + '/app/models/CTLSS_BONUS_DB'

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development':DevelopmentConfig,
    'production':ProductionConfig
}