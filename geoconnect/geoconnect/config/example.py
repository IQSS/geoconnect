import sys
import os


PROJECT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), '../')
TEST_SETUP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), '../../', 'test_setup' )

DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

#TEMPLATE_DIRS = ( os.path.join(PROJECT_DIR, 'templates')\
#                , os.path.join(PROJECT_DIR,  '../gis_shapefiles', 'templates')\
#                )
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(TEST_SETUP_DIR, 'test_db',  'some-db.sqlite3'),
    }
}

SECRET_KEY = 'some-secret-key'

SITE_ID = 1 

LOGIN_URL = "admin:index"


# Used for working with GIS files
#   example: extracting shapefiles
# Needs to be writable by application
# Cleaned out by cron job
#
GISFILE_SCRATCH_WORK_DIRECTORY = os.path.join(TEST_SETUP_DIR, 'gis_scratch_work')

MEDIA_ROOT = os.path.join(TEST_SETUP_DIR, 'media_root' )
MEDIA_URL = '/media/'

STATICFILES_DIRS = (os.path.join(PROJECT_DIR, "static") ,)  # original file source
STATIC_ROOT = os.path.join(TEST_SETUP_DIR, 'static_root') # where files gathered and served from
STATIC_URL = '/static/' # url for static files


SESSION_COOKIE_NAME = 'geo_connect_dev'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    #'core',
    'style_layer_information',
    'gis_basic_file',
    'gis_shapefiles',
    'worldmap_import',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(TEST_SETUP_DIR, 'logs', 'geoconnect.log'),
            'formatter': 'verbose'
        },
        'console':{
                   'level': 'DEBUG',
                   'class': 'logging.StreamHandler',
                   'formatter': 'simple'
               },
       'console':{
                'level':'INFO',
                'class':'logging.StreamHandler',
                'stream': sys.stdout
            },
            'console':{
                     'level':'ERROR',
                     'class':'logging.StreamHandler',
                     'stream': sys.stdout
                 },
    },
    'loggers': {
        'django': {
            'handlers':['file', 'console'],
            'propagate': True,
            'level':'DEBUG',
        },
    'geoconnect': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
        },
    }
}
