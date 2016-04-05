from __future__ import print_function
import os, sys
from os.path import dirname, join, abspath, isdir

if __name__=='__main__':
    PROJECT_ROOT = dirname(dirname(abspath(__file__)))
    paths = [ join(PROJECT_ROOT, 'geoconnect')\
            , join(PROJECT_ROOT, 'geoconnect', 'geoconnect')\
            , '/home/ubuntu/.virtualenvs/geoconnect/lib/python2.7/site-packages'\
            ]
    paths = [p for p in paths if isdir(p)]
    for p in paths:
        sys.path.append(p)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geoconnect.settings.production")

from django.conf import settings

#from django.core.mail import send_mail
#from django.template.loader import render_to_string

from geo_utils.stale_data_remover import StaleDataRemover

"""
# sudo crontab -e
MAILTO=raman_prasad@harvard.edu
9 * * * * /usr/bin/python /home/ubuntu/code/geoconnect/task_script/prune_scratch_directories.py

"""


if __name__=='__main__':
    sdr = StaleDataRemover()
    sdr.remove_stale_worldmap_data()
    sdr.remove_stale_dataverse_data()
