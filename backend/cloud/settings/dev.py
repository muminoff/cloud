from .base import *

# Debug
DEBUG = True

# Databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'cloud',
        'HOST': '',
        'PORT': '',
        'USER': 'cloud',
        'PASSWORD': 'cloud',
    }
}
