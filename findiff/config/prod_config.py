from findiff.common.class_utils import Config

DEBUG = False

ALLOWED_HOSTS = ['*']

MYSQL = Config(
    host='mysql',
    port='3306',
    user='root',
    password='MS5Qr5dGCdgqj',
    db='findiff',
)

STATIC_URL = '/static/'

STATIC_ROOT = '/data/static'

MEDIA_URL = '/media/'

MEDIA_ROOT = '/data/media'
