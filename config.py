from os import environ

FLASK_ENV = 'production'
SECRET_KEY = environ.get('SECRET_KEY')
TESTING = False
DEBUG = False
SQLALCHEMY_DATABASE_URI = 'sqlite:///bible.sqlite'
SQLALCHEMY_TRACK_MODIFICATIONS = False
