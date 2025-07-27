import os

class Config:
    SECRET_KEY = os.getenv('forecast', 'padrao-dev')
    DEBUG = False

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False