"""Development settings and globals."""

from __future__ import absolute_import
import json
import sys
from os import makedirs
from os.path import join, normpath, isdir, isfile

from .base import *

# Store uploaded files, logs, etc, etc
TEST_SETUP_DIR = normpath(join(SITE_ROOT, 'test_setup'))
####################### DATAVERSE_INFO_REPOSITORY_PATH
#
# Path to additional repository: https://github.com/IQSS/shared-dataverse-information
# Used for dataverse/worldmap communication.  Validate data passed via api, etc
#
#

DATAVERSE_INFO_REPOSITORY_PATH = '/Users/rmp553/Documents/iqss-git/shared-dataverse-information/'
if isdir(DATAVERSE_INFO_REPOSITORY_PATH):
    #raise Exception('Directory not found for repository "shared-dataverse-information" #(https://github.com/IQSS/shared-dataverse-information)\ndirectory in settings: %s' % #DATAVERSE_INFO_REPOSITORY_PATH)
    sys.path.append(DATAVERSE_INFO_REPOSITORY_PATH)

####################### END: DATAVERSE_INFO_REPOSITORY_PATH


STATIC_ROOT =join(TEST_SETUP_DIR, 'assets') # where files gathered and served from

MEDIA_ROOT = join(TEST_SETUP_DIR, 'media' )

########## DEBUG CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = True

ALLOWED_HOSTS = ('localhost', '127.0.0.1')


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
        'LOCATION': 'geo-local-snowflake',
    }
}
########## END CACHE CONFIGURATION

########## TOOLBAR CONFIGURATION
# See: http://django-debug-toolbar.readthedocs.org/en/latest/installation.html#explicit-setup
INSTALLED_APPS += (
    'storages',
)

########## Amazon S3 file storages
"""
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
from . import local_aws_creds
AWS_STORAGE_BUCKET_NAME = local_aws_creds.AWS_STORAGE_BUCKET_NAME
AWS_ACCESS_KEY_ID = local_aws_creds.AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = local_aws_creds.AWS_SECRET_ACCESS_KEY
"""
########## END Amazon S3 file storages



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

# Set Template debug to True
try:
    TEMPLATES[0]['OPTIONS']['debug'] = True
except:
    assert False, """Make sure TEMPLATES list is set with 1 entry that has an OPTIONS dict.
e.g. TEMPLATES = [ { 'OPTIONS' : { 'debug' : True }}]"""

########### DIRECTORY TO STORE DATA FILES COPIES FROM DV
# Do NOT make this directory accessible to a browser
#
DV_DATAFILE_DIRECTORY = join(TEST_SETUP_DIR, 'dv_datafile_directory')

########## GISFILE_SCRATCH_WORK_DIRECTORY
# Used for opening up files for processing, etc
GISFILE_SCRATCH_WORK_DIRECTORY = join(TEST_SETUP_DIR, 'gis_scratch_work')
########## END GISFILE_SCRATCH_WORK_DIRECTORY

##### RETRIEVE WORLDMAP PARAMS
# dev worldmap on AWS
# RETRIEVE WORLDMAP JSON INFO
WORLDMAP_SECRETS_FNAME = join( dirname(abspath(__file__)), "worldmap_secrets_local2.json")
#WORLDMAP_SECRETS_FNAME = join( dirname(abspath(__file__)), "worldmap_secrets_dev2.json")
#WORLDMAP_SECRETS_FNAME = join( dirname(abspath(__file__)), "worldmap_secrets_prod3.json")
if not isfile(WORLDMAP_SECRETS_FNAME):
    raise Exception('worldmap_secrets_fname JSON file not found: %s' % WORLDMAP_SECRETS_FNAME)

try:
    WORLDMAP_SECRETS_JSON = json.loads(open(WORLDMAP_SECRETS_FNAME, 'r').read())
except:
    raise Exception('Could not parse worldmap_secrets_fname JSON file: %s' % WORLDMAP_SECRETS_FNAME)


WORLDMAP_SERVER_URL = WORLDMAP_SECRETS_JSON['WORLDMAP_SERVER_URL']
WORLDMAP_ACCOUNT_USERNAME = WORLDMAP_SECRETS_JSON['WORLDMAP_ACCOUNT_USERNAME']
WORLDMAP_ACCOUNT_PASSWORD = WORLDMAP_SECRETS_JSON['WORLDMAP_ACCOUNT_PASSWORD']
WORLDMAP_ACCOUNT_AUTH = (WORLDMAP_ACCOUNT_USERNAME, WORLDMAP_ACCOUNT_PASSWORD)

WORLDMAP_EMBED_FORCE_HTTPS = False

##########  END WORLDMAP TOKEN / SERVER


# Only use for running locally
# Makes dataverse installation name unique
# to avoid name clashes on WorldMap
FORCE_UNIQUE_DEV_INSTALLATION_NAME = True


########## DATAVERSE_SERVER_URL
# Used to make API calls
# e.g.  http://dvn-build.hmdc.harvard.edu/
#
DATAVERSE_TOKEN_KEYNAME = 'GEOCONNECT_TOKEN'
DATAVERSE_SERVER_URL = 'http://127.0.0.1:8080'
DATAVERSE_METADATA_UPDATE_API_PATH =  '/api/worldmap/update-layer-metadata/' #DATAVERSE_SERVER_URL + '/api/worldmap/layer-update/'
##########  END DATAVERSE_SERVER_URL


########## LOGGING
GEOLOG_DIRNAME = join(TEST_SETUP_DIR, 'logs')
if not isdir(GEOLOG_DIRNAME):
    makedirs(GEOLOG_DIRNAME)
LOGGING = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple2': {
            'format': '%(levelname)s %(module)s %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple2'
            },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': join(GEOLOG_DIRNAME, 'geolog.log'),
            'formatter': 'simple'
            },
        },
    'loggers': {
        'gc_apps': {
               'handlers': ['console', 'file'],
               'level': 'DEBUG',
               'propagate': True
           },
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': False,
            },
        },
        'geoconnect': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
            },
    }

# make all loggers use the console.
#for logger in LOGGING['loggers']:
#   LOGGING['loggers'][logger]['handlers'] = ['console']
#LOGGING['loggers']['']['handlers'] = ['console']
