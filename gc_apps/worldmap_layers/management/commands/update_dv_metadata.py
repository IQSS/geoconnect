"""
Script to update the WorldMap metadata on Dataverse via a Dataverse API endpoint.
- Includes a variable delay that defaults to 3 seconds.
    - The delay allows the retrieval of a map PNG (thumbnail).  Without the delay,
geoserver may throw a 500
"""
from __future__ import print_function
import time

from django.core.management.base import BaseCommand#, CommandError
from django.conf import settings
from gc_apps.dv_notify.metadata_updater import MetadataUpdater
from gc_apps.geo_utils.msg_util import msg, msgt, dashes

class Command(BaseCommand):
    # Show this when the user types help
    help = ('Update the WorldMap metadata on Dataverse via a Dataverse API'
            ' endpoint.  Using the md5 of the WorldMapLayerInfo.'
            ' Note: This is used internally in lieu of a task queue')

    def add_arguments(self, parser):
        #parser.add_argument('poll_id', nargs='\d', type=str)

        #parser.add_argument('--md5', dest='worldmap_info_md5', action='append')
        parser.add_argument(
            '--md5',
            action='store',
            dest='worldmap_info_md5',
            help='Specify the md5 of the of the WorldMapLayerInfo object')

        parser.add_argument(
            '--type',
            action='store',
            dest='file_type',
            default=None,
            help='Specify the type of the of the WorldMapLayerInfo object')

        parser.add_argument(
            '--delay',
            type=int,
            dest='delay_seconds',
            default=3,
            help='Specify the seconds to wait between update attempts. (Default is 3)')

        parser.add_argument(
            '--num_attempts',
            type=int,
            dest='num_attempts',
            default=3,
            help='Specify the number of update attempts to try. (Default is 3)')

    def handle(self, *args, **options):

        print (options)

        # For Retrieving the WorldMap Layer Info stored in Geoconnect
        #
        worldmap_info_md5 = options.get('worldmap_info_md5', None)
        if worldmap_info_md5 is None:
            error_note = "Please specify the md5 of the WorldMapLayerInfo object"
            msg(error_note)
            return

        # File type, to differntiate which WorldMap Layer Info is stored in Geoconnect
        #
        file_type = options.get('file_type', None)
        if file_type is None:
            error_note = "Please specify the file type. e.g. --type=tabular"
            msg(error_note)
            return

        delay_seconds = options.get('delay_seconds')
        try:
            delay_seconds = int(delay_seconds)
        except ValueError:
            error_note = "Please use an integer for 'delay_seconds'"
            msg(error_note)
            return
        except TypeError:
            error_note = "Please use an integer for 'delay_seconds'"
            msg(error_note)
            return

        num_attempts = options.get('num_attempts')
        try:
            num_attempts = int(num_attempts)
        except ValueError:
            error_note = "Please use an integer for 'num_attempts'"
            msg(error_note)
            return
        except TypeError:
            error_note = "Please use an integer for 'num_attempts'"
            msg(error_note)
            return


        for attempt_num in range(1, num_attempts+1):

            msg('(Attempt %s) Pausing for %s second(s)' % (attempt_num, delay_seconds))
            time.sleep(delay_seconds)

            success, err_info = MetadataUpdater.run_metadata_update_with_thumbnail_check(\
                                worldmap_info_md5, file_type)
            msg('success: %s' % success)
            msg('err_info: %s' % err_info)
            if success is True:
                break
