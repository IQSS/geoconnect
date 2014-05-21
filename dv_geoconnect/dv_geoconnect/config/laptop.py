import os


PROJECT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), )

DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

#TEMPLATE_DIRS = ( os.path.join(PROJECT_DIR, 'templates')\
#                , os.path.join(PROJECT_DIR,  '../gis_shapefiles', 'templates')\
#                )

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_DIR, '../testdb/db.sqlite3'),
    }
}

SECRET_KEY = '-*!l6ue971ie=t=+=)jq=&gcr=6ceo3f90z7e1z-_$3olv5(6k'


# Used for working with GIS files
#   example: extracting shapefiles
# Needs to be writable by application
# Cleaned out by cron job
#
GISFILE_SCRATCH_WORK_DIRECTORY = os.path.join(PROJECT_DIR, 'gis_scratch_work')

MEDIA_ROOT = os.path.join(PROJECT_DIR, 'media_root' )
MEDIA_URL = '/media/'

STATICFILES_DIRS = (os.path.join(PROJECT_DIR, "static") ,)  # original file source
STATIC_ROOT = os.path.join(PROJECT_DIR, 'static_root') # where files gathered and served from
STATIC_URL = '/static/' # url for static files

SESSION_COOKIE_NAME = 'geo_connect_dev'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    'style_layer_information',
    'gis_basic_file',
    'gis_shapefiles',
    'worldmap_import',
)
