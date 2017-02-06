"""
WSGI config for Geoconnect on Heroku

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
"""

import os

from django.core.wsgi import get_wsgi_application
from whitenoise.django import DjangoWhiteNoise

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "miniverse.settings.heroku_dev")

application = get_wsgi_application()
application = DjangoWhiteNoise(application)
