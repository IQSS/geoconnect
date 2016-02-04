"""Production settings and globals."""

from __future__ import absolute_import

from os.path import join, normpath, isdir, isfile
import json
import sys

from .base import *

"""
DATAVERSE_INFO_REPOSITORY_PATH = '/webapps/code/shared-dataverse-information'
if not isdir(DATAVERSE_INFO_REPOSITORY_PATH):
    raise Exception('Directory not found for repository "shared-dataverse-information" (https://github.com/IQSS/shared-dataverse-information)\ndirectory in settings: %s' % DATAVERSE_INFO_REPOSITORY_PATH)
sys.path.append(DATAVERSE_INFO_REPOSITORY_PATH)
"""

SITENAME = "geoconnect"

SITEURL = "http://geoconnect.datascience.iq.harvard.edu"

# RETRIEVE WORLDMAP JSON INFO
GEOCONNECT_SECRETS_FNAME = join( dirname(abspath(__file__)), "geoconnect_secrets_prod.json")
if not isfile(GEOCONNECT_SECRETS_FNAME):
    raise Exception('Geoconnect settings JSON file not found: %s' % GEOCONNECT_SECRETS_FNAME)

try:
    JSON_SECRETS = json.loads(open(GEOCONNECT_SECRETS_FNAME, 'r').read())
except:
    raise Exception('Could not parse Geoconnect settings JSON file: %s' % GEOCONNECT_SECRETS_FNAME)


# Store uploaded files, logs, etc, etc
GEOCONNECT_NOT_ACCESSIBLE_FILES_DIR = JSON_SECRETS['GEOCONNECT_NOT_ACCESSIBLE_FILES_DIR']
GEOCONNECT_LOGS_DIR =  join(GEOCONNECT_NOT_ACCESSIBLE_FILES_DIR, 'logs')

STATIC_ROOT = '/var/www/geoconnect/static' #join(GEOCONNECT_FILES_DIR, 'assets') # where files gathered and served from

MEDIA_ROOT = '/var/www/geoconnect/media/'   #' join(GEOCONNECT_FILES_DIR, 'media' )

########## URL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
#ROOT_URLCONF = '%s.urls' % SITE_NAME
ROOT_URLCONF = '%s.urls_prod' % SITE_NAME

########## END URL CONFIGURATION

#ALLOWED_HOSTS = ['54.68.229.158']
ALLOWED_HOSTS = JSON_SECRETS['ALLOWED_HOSTS']


ADMINS = JSON_SECRETS['ADMINS']
########## DEBUG CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
#DEBUG = False
DEBUG = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
TEMPLATE_DEBUG = DEBUG
########## END DEBUG CONFIGURATION


########## EMAIL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host
EMAIL_HOST = JSON_SECRETS['EMAIL_SETTINGS']['EMAIL_HOST']

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host-user
EMAIL_HOST_USER = JSON_SECRETS['EMAIL_SETTINGS']['EMAIL_HOST_USER']

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host-password
EMAIL_HOST_PASSWORD = JSON_SECRETS['EMAIL_SETTINGS']['EMAIL_HOST_PASSWORD']

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-port
EMAIL_PORT = JSON_SECRETS['EMAIL_SETTINGS']['EMAIL_PORT']
#environ.get('EMAIL_PORT', 587)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-subject-prefix
EMAIL_SUBJECT_PREFIX = '[%s] ' % SITE_NAME

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-use-tls
EMAIL_USE_TLS = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#server-email
SERVER_EMAIL = EMAIL_HOST_USER
########## END EMAIL CONFIGURATION


########## DATABASE CONFIGURATION
DATABASES = {
    'default': {
        'ENGINE': JSON_SECRETS['DATABASE_SETTINGS']['ENGINE'],
        'NAME': JSON_SECRETS['DATABASE_SETTINGS']['NAME'],
        'USER': JSON_SECRETS['DATABASE_SETTINGS']['USER'],
        'PASSWORD': JSON_SECRETS['DATABASE_SETTINGS']['PASSWORD'],
        'HOST': JSON_SECRETS['DATABASE_SETTINGS']['HOST'],
        'PORT': JSON_SECRETS['DATABASE_SETTINGS']['PORT'],
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
    #'debug_toolbar',
    #'djcelery',
    #'kombu.transport.django',
)

#MIDDLEWARE_CLASSES += (
#   'debug_toolbar.middleware.DebugToolbarMiddleware',
#)
#

########## SECRET CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = JSON_SECRETS['SECRET_KEY']
########## END SECRET CONFIGURATION

#DEBUG_TOOLBAR_PATCH_SETTINGS = False

# http://django-debug-toolbar.readthedocs.org/en/latest/installation.html
#INTERNAL_IPS = ('127.0.0.1',)
########## END TOOLBAR CONFIGURATION

########## SESSION_COOKIE_NAME
SESSION_COOKIE_NAME = 'geoconnect_prod'
########## END SESSION_COOKIE_NAME

########## LOGIN_URL
# To use with decorator @login_required
LOGIN_URL = "admin:index"
########## END LOGIN_URL


########## DATAVERSE_SERVER_URL
# Used to make API calls
# e.g.  http://dvn-build.hmdc.harvard.edu/
#
DATAVERSE_SERVER_URL = JSON_SECRETS['DATAVERSE_SERVER_URL']
DATAVERSE_METADATA_UPDATE_API_PATH =  '/api/worldmap/update-layer-metadata/'
#DATAVERSE_METADATA_UPDATE_API_PATH =  '/api/worldmap/update-layer-metadata/?key=pete' #DATAVERSE_SERVER_URL + '/api/worldmap/layer-update/'
########## DATAVERSE_SERVER_URL

########### DIRECTORY TO STORE DATA FILES COPIES FROM DV
# Do NOT make this directory accessible to a browser
#
DV_DATAFILE_DIRECTORY = join(GEOCONNECT_NOT_ACCESSIBLE_FILES_DIR, 'dv_datafile_directory')

########## GISFILE_SCRATCH_WORK_DIRECTORY
# Used for opening up files for processing, etc
GISFILE_SCRATCH_WORK_DIRECTORY = join(GEOCONNECT_NOT_ACCESSIBLE_FILES_DIR, 'gis_scratch_work')
########## END GISFILE_SCRATCH_WORK_DIRECTORY

########## WORLDMAP TOKEN/SERVER | DATAVERSE TOKEN AND SERVER
#

# RETRIEVE WORLDMAP JSON INFO
WORLDMAP_SECRETS_FNAME = join( dirname(abspath(__file__)), "worldmap_secrets_prod2.json")
#WORLDMAP_SECRETS_FNAME = join( dirname(abspath(__file__)), "worldmap_secrets_dev.json")
if not isfile(WORLDMAP_SECRETS_FNAME):
    raise Exception('worldmap_secrets_fname JSON file not found: %s' % WORLDMAP_SECRETS_FNAME)

try:
    WORLDMAP_SECRETS_JSON = json.loads(open(WORLDMAP_SECRETS_FNAME, 'r').read())
except:
    raise Exception('Could not parse worldmap_secrets_fname JSON file: %s' % WORLDMAP_SECRETS_FNAME)


#WORLDMAP_TOKEN_FOR_DATAVERSE = WORLDMAP_SECRETS_JSON['WORLDMAP_TOKEN_FOR_DATAVERSE']
WORLDMAP_SERVER_URL = WORLDMAP_SECRETS_JSON['WORLDMAP_SERVER_URL']
WORLDMAP_ACCOUNT_USERNAME = WORLDMAP_SECRETS_JSON['WORLDMAP_ACCOUNT_USERNAME']
WORLDMAP_ACCOUNT_PASSWORD = WORLDMAP_SECRETS_JSON['WORLDMAP_ACCOUNT_PASSWORD']
WORLDMAP_ACCOUNT_AUTH = (WORLDMAP_ACCOUNT_USERNAME, WORLDMAP_ACCOUNT_PASSWORD)

########## END WORLDMAP TOKEN/SERVER | DATAVERSE TOKEN AND SERVER

########## LOGGING

LOGGING = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': join(GEOCONNECT_LOGS_DIR, 'geolog.log'),
            'formatter': 'verbose'
            },
        },
    'loggers': {

        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': False,
            },
        },
        'geoconnect': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
        'apps': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
            },
    }
