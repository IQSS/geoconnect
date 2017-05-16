"""Common settings and globals."""


from os.path import abspath, basename, dirname, join, normpath
from sys import path


########## PATH CONFIGURATION
# Absolute filesystem path to the Django project directory:
DJANGO_ROOT = dirname(dirname(abspath(__file__)))

# Absolute filesystem path to the top-level project folder:
SITE_ROOT = dirname(DJANGO_ROOT)

# Site name:
SITE_NAME = 'geoconnect'    #basename(DJANGO_ROOT)

# Project test files
# Absolute filesystem path to the Django project directory:
PROJECT_TEST_FILES_DIR = join(SITE_ROOT, 'test_files')

# Add our project to our pythonpath, this way we don't need to type our project
# name in our dotted import paths:
path.append(DJANGO_ROOT)
########## END PATH CONFIGURATION


####################### DATAVERSE_INFO_REPOSITORY_PATH
#
# Path to additional repository: https://github.com/IQSS/shared-dataverse-information
# Used for dataverse/worldmap communication.  Validate data passed via api, etc
#
#DATAVERSE_INFO_REPOSITORY_PATH = '/home/ubuntu/code/shared-dataverse-information'
####################### END: DATAVERSE_INFO_REPOSITORY_PATH


########## DEBUG CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = True



########## AUTH_USER_MODEL
#AUTH_USER_MODEL = 'dataverse_user.DataverseUser'
########## END AUTH_USER_MODEL


########## MANAGER CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = (('Raman Prasad', 'raman_prasad@harvard.edu'),)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS
########## END MANAGER CONFIGURATION


########## DATABASE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}
########## END DATABASE CONFIGURATION


########## GENERAL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#time-zone
TIME_ZONE = 'America/New_York'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = 'en-us'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True
########## END GENERAL CONFIGURATION


########## MEDIA CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = normpath(join(SITE_ROOT, 'media'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = '/media/'
########## END MEDIA CONFIGURATION


########## STATIC FILE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = normpath(join(SITE_ROOT, 'assets'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = (
    normpath(join(SITE_ROOT, 'static')),
)

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)
########## END STATIC FILE CONFIGURATION


########## SECRET CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Note: This key should only be used for development and testing.
SECRET_KEY = r"8^u6_^t1c6m2$1^46pg7c-LAPTOP-KEY-&9^^y8huzyj2g0)qd8+7mqlj6dw5"
########## END SECRET CONFIGURATION


########## SITE CONFIGURATION
# Hosts/domain names that are valid for this site
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []
########## END SITE CONFIGURATION


########## FIXTURE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-FIXTURE_DIRS
FIXTURE_DIRS = (
    normpath(join(SITE_ROOT, 'fixtures')),
)
########## END FIXTURE CONFIGURATION


########## TEMPLATE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            normpath(join(SITE_ROOT, 'templates')),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
########## END TEMPLATE CONFIGURATION




########## URL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = '%s.urls' % SITE_NAME
########## END URL CONFIGURATION


########## APP CONFIGURATION
DJANGO_APPS = (
    # Default Django apps:
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Useful template tags:
     'django.contrib.humanize',

    # Admin panel and documentation:
    'django.contrib.admin',
    # 'django.contrib.admindocs',
)

# Apps specific for this project go here.
LOCAL_APPS = (
    'django_cleanup',   # delete files linked by FileField objects

    'shared_dataverse_information.layer_classification',
    'shared_dataverse_information.shapefile_import',
    #'dataverse_info',
    #'gc_apps.classification',       # used for styling WorldMap layers
    'gc_apps.content_pages',
    'gc_apps.registered_dataverse',    # relies on gis_basic_file
    #'gc_apps.style_layer_information',

    'gc_apps.worldmap_layers', # abstract model
    'gc_apps.gis_basic_file',
    'gc_apps.gis_shapefiles',
    'gc_apps.gis_tabular',
    'gc_apps.worldmap_connect',
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS
########## END APP CONFIGURATION

DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

########## LOGGING CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#logging
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
########## END LOGGING CONFIGURATION


########## WSGI CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = '%s.wsgi.application' % SITE_NAME
########## END WSGI CONFIGURATION

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Only use for running locally
# Makes dataverse installation name unique
# to avoid name clashes on WorldMap
FORCE_UNIQUE_DEV_INSTALLATION_NAME = False

########## SESSION_COOKIE_NAME
SESSION_COOKIE_NAME = 'geoconnect_local'
########## END SESSION_COOKIE_NAME

########## GISFILE_SCRATCH_WORK_DIRECTORY
# Used for opening up files for processing, etc
GISFILE_SCRATCH_WORK_DIRECTORY = None
########## END GISFILE_SCRATCH_WORK_DIRECTORY

# Time used by scripts to remove stale data objects
#   e.g. Objects removed if they were created more
#   than 'x' minutes ago--where 'x' is the variable below
#
STALE_DATA_SECONDS_TO_EXPIRATION = 60 #* 60 * 24 * 2     # 2 DAYS


########## LOGIN_URL
# To use with decorator @login_required
LOGIN_URL = "admin:index"
########## END LOGIN_URL

########## DATAVERSE_SERVER_URL
# Used to make API calls
# e.g.  http://dvn-build.hmdc.harvard.edu/
#
DATAVERSE_TOKEN_KEYNAME = 'GEOCONNECT_TOKEN'
DATAVERSE_SERVER_URL = 'http://127.0.0.1:8080'
DATAVERSE_METADATA_UPDATE_API_PATH =  '/api/worldmap/update-layer-metadata/' #DATAVERSE_SERVER_URL +

########### DIRECTORY TO STORE DATA FILES COPIES FROM DV
# Do NOT make this directory accessible to a browser
#
DV_DATAFILE_DIRECTORY = None

########## END DATAVERSE_SERVER_URL

BROKER_URL = 'django://'

########## WORLDMAP CONNECTION INFO
WORLDMAP_SERVER_URL = None  # e.g. 'http://107.22.231.227'
WORLDMAP_ACCOUNT_USERNAME = None
WORLDMAP_ACCOUNT_PASSWORD = None

WORLDMAP_DEFAULT_TIMEOUT = 4 * 60 # seconds
WORLDMAP_SHORT_TIMEOUT = 2 * 60 # seconds, for non-layer making requests

# Go and get info from WorldMap instead of using saved info
WORLDMAP_LAYER_EXPIRATION = 15 * 60 # 15 minutes

JOIN_TARGET_UPDATE_TIME = 1 * 60 # 10 minutes

# Make sure links to the embedded map and legend use https
WORLDMAP_EMBED_FORCE_HTTPS = True
