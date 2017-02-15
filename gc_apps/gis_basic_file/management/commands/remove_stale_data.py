"""
Delete old S3 files and related geoconnect objects
"""
from __future__ import print_function
from django.core.management.base import BaseCommand#, CommandError
from django.conf import settings

from gc_apps.geo_utils.stale_data_remover import StaleDataRemover
from gc_apps.geo_utils.msg_util import msg, msgt, dashes

class Command(BaseCommand):
    # Show this when the user types help
    help = """Delete old files and related geoconnect objects. This applies to any objects not modified in the time specified by "settings.STALE_DATA_SECONDS_TO_EXPIRATION".  Note: If S3 is used for settings.DEFAULT_FILE_STORAGE, the stale S3 objects will be deleted."""

    def add_arguments(self, parser):
        parser.add_argument(
            '--really_delete',
            action='store_true',
            dest='really_delete',
            default=False,
            help='Default is to check for stale objects.  Set this to True to delete them',
        )
        parser.add_argument(
            '--email_notice',
            action='store_true',
            dest='email_notice',
            default=False,
            help='Email the results to the Django ADMINS specified in settings',
        )

    def handle(self, *args, **options):

        really_delete = options.get('really_delete', False)
        email_notice = options.get('email_notice', False)

        dashes()
        if really_delete:
            msg('Check for old objects and DELETE them')
        else:
            msg('Check for old objects but DO NOT delete them')
        stale_data_remover = StaleDataRemover(really_delete=really_delete)

        stale_data_remover.remove_stale_data(\
            settings.STALE_DATA_SECONDS_TO_EXPIRATION)

        if email_notice is True:
            stale_data_remover.send_email_notice()
