from .base import *  # noqa: F403

DEBUG = True

ALLOWED_HOSTS = ['*']
SITE_URL = "http://127.0.0.1:8080/"


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'previniendo',
        'USER': 'previniendo',
        'PASSWORD': 'previniendo',
        'HOST': 'dev-previniendo-db',
        'PORT': '5432',
    }
}

CORS_ORIGIN_ALLOW_ALL = True

INSTALLED_APPS += (  # noqa: F405
    'django_extensions',
)

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = (  # noqa: F405
    'rest_framework.renderers.JSONRenderer',
    'rest_framework.renderers.BrowsableAPIRenderer'
)

MEDIA_URL = '/media/'
STATIC_URL = 'media/'
