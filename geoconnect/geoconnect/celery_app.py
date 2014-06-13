from __future__ import absolute_import

import os
print '-'*30
from celery import Celery
print 'l0'

from django.conf import settings
print 'l1'

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geoconnect.settings')
print 'l2'
app = Celery('geoconnect')
print 'l3'

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
print 'l4'
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
print 'l5'
print dir(settings)
app.conf.update(
    CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend',
)
app.conf.update(
    CELERY_RESULT_BACKEND='djcelery.backends.cache:CacheBackend',
)

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))