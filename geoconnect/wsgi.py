"""
WSGI config for geoconnect project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
import sys

sys.stdout = sys.stderr     # send print statements to the apache logs

prod_paths = ['/home/ubuntu/code/geoconnect/'\
    , '/home/ubuntu/code/geoconnect/geoconnect']

for p in prod_paths:
    if os.path.isdir(p): sys.path.append(p)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geoconnect.settings.production")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()


