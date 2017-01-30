from __future__ import print_function
import os, sys
from os.path import dirname, join, abspath, isdir

if __name__=='__main__':
    PROJECT_ROOT = dirname(dirname(abspath(__file__)))
    paths = [ PROJECT_ROOT,\
            join(PROJECT_ROOT, 'geoconnect'),\
            join(PROJECT_ROOT, 'geoconnect', 'geoconnect'),\
            '/home/ubuntu/.virtualenvs/geoconnect/lib/python2.7/site-packages'\
            ]
    paths = [p for p in paths if isdir(p)]
    for p in paths:
        sys.path.append(p)

    os.environ["DJANGO_SETTINGS_MODULE"] = "geoconnect.settings.production"


from gc_apps.geo_utils.stale_data_remover import StaleDataRemover

"""
# sudo crontab -e
MAILTO=raman_prasad@harvard.edu
9 * * * * /webapps/virtualenvs/geoconnect/bin/python /webapps/code/geoconnect/task_scripts/remove_stale_data.py
"""


if __name__=='__main__':
    sdr = StaleDataRemover()
    sdr.remove_stale_worldmap_data()
    sdr.remove_stale_dataverse_data()
    sdr.send_email_notice()
