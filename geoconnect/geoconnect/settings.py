"""
Django settings for geoconnect project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os, sys
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

gis_shapefiles_app_pth = os.path.join(BASE_DIR, '../')
sys.path.append(gis_shapefiles_app_pth)


import config.laptop as config

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config.SECRET_KEY


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config.DEBUG

TEMPLATE_DEBUG = config.DEBUG

ALLOWED_HOSTS = config.ALLOWED_HOSTS

#TEMPLATE_DIRS = config.TEMPLATE_DIRS
TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
#    "/home/html/templates/lawrence.com",
#    "/home/html/templates/default",
)

# Application definition

INSTALLED_APPS = config.INSTALLED_APPS

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'geoconnect.urls'

WSGI_APPLICATION = 'geoconnect.wsgi.application'

# Used for working with GIS files
#   example: extracting shapefiles
# Needs to be writable by application
# Cleaned out by cron job
#
GISFILE_SCRATCH_WORK_DIRECTORY = config.GISFILE_SCRATCH_WORK_DIRECTORY

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = config.DATABASES

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

SITE_ID = config.SITE_ID

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
MEDIA_ROOT = config.MEDIA_ROOT
MEDIA_URL = config.MEDIA_URL


STATIC_URL = config.STATIC_URL
STATICFILES_DIRS = config.STATICFILES_DIRS
STATIC_ROOT = config.STATIC_ROOT


XLOGGING = {
    'version': 1,
    'root': {'level': 'DEBUG' if DEBUG else 'INFO'},
}

SESSION_COOKIE_NAME = config.SESSION_COOKIE_NAME

LOGGING = config.LOGGING