from __future__ import print_function
import os, sys
from os.path import dirname, join, abspath

if __name__=='__main__':
    PROJECT_ROOT = dirname(dirname(abspath(__file__)))
    paths = [ join(PROJECT_ROOT, 'geoconnect')\
            , join(PROJECT_ROOT, 'geoconnect', 'geoconnect')\
            , '/home/ubuntu/.virtualenvs/geoconnect/lib/python2.7/site-packages'\
            ]
    for p in paths:
        sys.path.append(p)
    
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geoconnect.settings.production")

from django.conf import settings

from django.core.mail import send_mail
from django.template.loader import render_to_string

from geo_utils.msg_util import *
from gc_apps.gis_basic_file.scratch_directory_services import ScratchDirectoryHelper

"""
# sudo crontab -e
MAILTO=raman_prasad@harvard.edu
9 * * * * /usr/bin/python /home/ubuntu/code/geoconnect/task_script/prune_scratch_directories.py

"""

class ScratchDirectoryPruner:
    
    def __init__(self, max_directory_age_in_hours=6):
        self.max_directory_age_in_hours = max_directory_age_in_hours
        self.run_delete()
        
    def run_delete(self):
        
        (names_of_deleted_dirs, names_failed_delete_dirs) =  ScratchDirectoryHelper.clear_scratch_directories(\
                                                        max_hours=self.max_directory_age_in_hours\
                                                    )
        self.send_email_notice( names_of_deleted_dirs, names_failed_delete_dirs)

    def send_email_notice(self, names_of_deleted_dirs, names_failed_delete_dirs):
        msgt('Send email notice!')

        if len(names_failed_delete_dirs) > 0:
            subject = '(err) GeoConnect: ScratchDirectoryPruner' 
        else:
            subject = '(ok) GeoConnect: ScratchDirectoryPruner' 
            
        if len(settings.ADMINS)==0:
            msg('No one to email! (no one in settings.ADMINS)')
            return

        to_addresses = map(lambda x: x[1], settings.ADMINS)
        if len(settings.ADMINS)==0:
            msg('No one to email! (no one in settings.ADMINS)')
            return
        
        d = dict(names_of_deleted_dirs=names_of_deleted_dirs\
                , names_failed_delete_dirs=names_failed_delete_dirs\
                 )     
        email_msg = render_to_string('task_scripts/prune_scratch_directories_email.txt', d)     
        msg(subject)
        msg(email_msg)
        from_email = to_addresses[0]

        send_mail(subject, email_msg, from_email, to_addresses, fail_silently=False)

        msg('email sent to: %s' % to_addresses)

        

if __name__=='__main__':
    sdh = ScratchDirectoryPruner()
