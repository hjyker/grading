from findiff.common.class_utils import Config

DEBUG = False

ALLOWED_HOSTS = ['*']

MYSQL = Config(
    host='mysql',
    port='3306',
    user='root',
    password='b2&Ydow3PzN',
    db='grading',
)

STATIC_URL = '/static/'

STATIC_ROOT = '/data/static'

MEDIA_URL = '/media/'

MEDIA_ROOT = '/data/media'
