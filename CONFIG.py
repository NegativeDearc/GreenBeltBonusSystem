__author__ = 'SXChen'

import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'WELCOME TO SIX_SIGMA TEAM'
    DATABASE_PATH = basedir + '/CLSS_BONUS_DB'

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development':DevelopmentConfig,
    'production':ProductionConfig
}