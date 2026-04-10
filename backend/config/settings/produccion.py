from .base import *  # noqa: F403, F401
import os

DEBUG = False
ALLOWED_HOSTS = ['165.22.149.77', 'previniendosst.co']

# En producción, si el servidor SMTP bloquea los puertos estándar (25, 465, 587),
# usamos 2525 por defecto para permitir envío sin cambiar código (puede anularse con la var de entorno EMAIL_PORT)
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 2525))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'previniendo',
        'USER': 'previniendo',
        'PASSWORD': 'Previniendo2025!',
        'HOST': '165.22.149.77',  # host-gateway from compose
        'PORT': '5432',
    }
}


MEDIA_ROOT = '/media/'  # Docker volume
STATIC_ROOT = "/public/"  # Docker volume

# En producción queremos que los fallos de envío de correo sean visibles
EMAIL_FAIL_RAISE = True
