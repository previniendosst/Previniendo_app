from .base import *  # noqa: F403, F401

DEBUG = False
ALLOWED_HOSTS = ['165.22.149.77', 'previniendosst.co']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'previniendo',
        'USER': 'previniendo',
        'PASSWORD': 'Previniendo2025!',
        'HOST': 'host.docker.internal',  # host-gateway from compose
        'PORT': '5432',
    }
}


MEDIA_ROOT = '/media/'  # Docker volume
STATIC_ROOT = "/public/"  # Docker volume
