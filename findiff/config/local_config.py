from findiff.common.class_utils import Config

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

INSTALLED_APPS = [
    'drf_yasg',
    'debug_toolbar',
]

INTERNAL_IPS = [
    'localhost',
    '127.0.0.1',
    '172.19.0.1',  # NOTE 如果使用 Docker 请加上 Docker 子网下的宿主机 IP，如 172.17.0.1
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

MYSQL = Config(
    host='mysql',
    port='3306',
    user='root',
    password='rootroot',
    db='findiff',
)

STATIC_URL = '/static/'

STATIC_ROOT = '/data/static'

MEDIA_URL = '/media/'

MEDIA_ROOT = '/data/media'
