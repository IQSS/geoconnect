import shutil
import os
from datetime import datetime, timedelta
from django.conf import settings
import re
import logging
from gc_apps.geo_utils.time_util import TIME_FORMAT_STRING

logger = logging.getLogger(__name__)

class FoliumDirectoryHelper:
    """Manage the directories for folium output.
    These directories are built under the settings.MEDIA_ROOT
    """

    @staticmethod
    def clear_scratch_directories(max_hours=6):
        """Delete all scratch directories not used within the 'max_hours'
        (A negative number could be used to delete all directories regardless of time)
        """

        # Deleting all older directories as defined by their folder name
        l = os.listdir(settings.MEDIA_ROOT)
        l = [x for x in l if re.search('\d{4}(-\d{4}){2}', x)]

        current_time = datetime.now()
        for dirname in l:
            print dirname
            try:
                dt = datetime.strptime(dirname[:14], TIME_FORMAT_STRING)
                time_diff = current_time - dt
                if time_diff.days > 0 or (time_diff.seconds/3600) > max_hours:
                    shutil.rmtree(os.path.join(settings.MEDIA_ROOT, dirname ))
            except:
                pass

    @staticmethod
    def delete_output_directory(folium_map):
        """If scratch directory exists, delete it
        return False    folium_map is None
        return True     directory doesn't exist
        return True     directory is deleted
        return False    failed to delete directory
        """
        if folium_map is None:
            logger.error('GIS file helper is None')
            return False

        if not FoliumDirectoryHelper._does_output_directory_exist(folium_map):
            return True

        try:
            shutil.rmtree(folium_map.folium_output_directory)
            return True
        except:
            logger.error('Failed to delete directory: %s:' % folium_map.folium_output_directory)
            return False

    @staticmethod
    def get_output_directory(folium_map):
        """Ensure that the scratch work directory exists
        Success - return the full path to the directory
        Fail - return None
        """
        if folium_map is None:
            return None

        # If directory exists, return it
        if FoliumDirectoryHelper._does_output_directory_exist(folium_map):
            return folium_map.folium_output_directory

        # If directory doesn't exist, create it
        if FoliumDirectoryHelper._make_output_directory(folium_map):
            return folium_map.folium_output_directory

        return None

    @staticmethod
    def _does_output_directory_exist(folium_map):
        """Check the attribute folium_output_directory:
            - Is it populated?
            - Does it contain a valid directory?
        """
        if folium_map is None:
            return False

        if folium_map.folium_output_directory and \
            os.path.isdir(folium_map.folium_output_directory):
            return True
        return False


    @staticmethod
    def _make_output_directory(folium_map):
        """For a GISDataFile object, create a scratch directory.
        Added to the base specified by the settings.MEDIA_ROOT
        Assumes that directory doesn't exist,
        Returns True or False
        """
        if folium_map is None:
            return False

        if not folium_map.id:
            folium_map.save()  # save to create id

        dirname = os.path.join(settings.MEDIA_ROOT\
                                , '%s__%s' % (datetime.today().strftime(TIME_FORMAT_STRING)\
                                                , folium_map.id)\
                                )

        if os.path.isdir(dirname):
            return True

        try:
            os.makedirs(dirname)
            folium_map.folium_output_directory = dirname
            folium_map.save()
            return True
        except:
            logger.critical('Failed to create directory: %s:' % dirname)
            return False
