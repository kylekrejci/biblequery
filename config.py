from os import environ

FLASK_ENV = 'production'
SECRET_KEY = environ.get('SECRET_KEY')
SESSION_TYPE = 'filesystem'
TESTING = False
DEBUG = False

