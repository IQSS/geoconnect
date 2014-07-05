"""Development settings and globals."""

from __future__ import absolute_import

from os.path import join, normpath

from .base import *

# Store uploaded files, logs, etc, etc
TEST_SETUP_DIR = join(dirname(dirname(DJANGO_ROOT)), 'test_setup')

STATIC_ROOT =join(TEST_SETUP_DIR, 'assets') # where files gathered and served from

MEDIA_ROOT = join(TEST_SETUP_DIR, 'media' )

########## DEBUG CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
TEMPLATE_DEBUG = DEBUG
########## END DEBUG CONFIGURATION


########## EMAIL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
########## END EMAIL CONFIGURATION


########## DATABASE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': normpath(join(TEST_SETUP_DIR, 'geodb.db3')),
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    },
   
}
########## END DATABASE CONFIGURATION


########## CACHE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
########## END CACHE CONFIGURATION

########## TOOLBAR CONFIGURATION
# See: http://django-debug-toolbar.readthedocs.org/en/latest/installation.html#explicit-setup
INSTALLED_APPS += (
    'debug_toolbar',
    #'djcelery',
    'kombu.transport.django', 
)

MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

DEBUG_TOOLBAR_PATCH_SETTINGS = False

# http://django-debug-toolbar.readthedocs.org/en/latest/installation.html
INTERNAL_IPS = ('127.0.0.1',)
########## END TOOLBAR CONFIGURATION

########## SESSION_COOKIE_NAME
SESSION_COOKIE_NAME = 'geoconnect_dev'
########## END SESSION_COOKIE_NAME

########## LOGIN_URL
# To use with decorator @login_required
LOGIN_URL = "admin:index"
########## END LOGIN_URL


########## DATAVERSE_SERVER_URL
# Used to make API calls
# e.g.  http://dvn-build.hmdc.harvard.edu/
#
DATAVERSE_SERVER_URL = 'http://127.0.0.1:8090'
########## DATAVERSE_SERVER_URL

########### DIRECTORY TO STORE DATA FILES COPIES FROM DV
# Do NOT make this directory accessible to a browser
#
DV_DATAFILE_DIRECTORY = join(TEST_SETUP_DIR, 'dv_datafile_directory')

########## GISFILE_SCRATCH_WORK_DIRECTORY
# Used for opening up files for processing, etc
GISFILE_SCRATCH_WORK_DIRECTORY = join(TEST_SETUP_DIR, 'gis_scratch_work')
########## END GISFILE_SCRATCH_WORK_DIRECTORY

#WORLDMAP_TOKEN_FOR_DV = 'JdPGVSga9yM8gt74ZpLp'
#WORLDMAP_SERVER_URL = 'http://107.22.231.227'

WORLDMAP_TOKEN_FOR_DV = 'JdPGVSga9yM8gt74ZpLp'
WORLDMAP_SERVER_URL = 'http://localhost:8000' #'http://127.0.0.1:8000'

