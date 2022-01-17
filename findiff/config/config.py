import os

ENV = os.getenv('ENV', 'dev')

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = []

MIDDLEWARE = []

INTERNAL_IPS = []

MYSQL = None

if ENV == 'dev':
    from .local_config import *  # noqa
elif ENV == 'prod':
    from .prod_config import *  # noqa
