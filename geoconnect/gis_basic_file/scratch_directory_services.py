import shutil
import os
from datetime import datetime, timedelta
from geoconnect import settings
import re
import logging

logger = logging.getLogger(__name__)

class ScratchDirectoryHelper:
    """Manage the scratch directories.
    These directories are built under the settings.GISFILE_SCRATCH_WORK_DIRECTORY 
    """
    TIME_FORMAT_STRING = '%Y-%m%d-%H%M'
    
    @staticmethod
    def clear_scratch_directories(max_hours=6):
        """Delete all scratch directories not used within the 'max_hours' 
        (A negative number could be used to delete all directories regardless of time)
        """

        # Deleting all older directories as defined by their folder name
        l = os.listdir(settings.GISFILE_SCRATCH_WORK_DIRECTORY)
        l = [x for x in l if re.search('\d{4}(-\d{4}){2}', x)]
        
        current_time = datetime.now()
        for dirname in l:
            print dirname
            try:
                dt = datetime.strptime(dirname[:14], ScratchDirectoryHelper.TIME_FORMAT_STRING)
                time_diff = current_time - dt
                if time_diff.days > 0 or (time_diff.seconds/3600) > max_hours:
                    shutil.rmtree(os.path.join(settings.GISFILE_SCRATCH_WORK_DIRECTORY, dirname ))
            except:
                pass
                
    @staticmethod
    def delete_scratch_work_directory(gis_data_file):
        """If scratch directory exists, delete it
        return False    gis_data_file is None 
        return True     directory doesn't exist 
        return True     directory is deleted
        return False    failed to delete directory
        """
        if gis_data_file is None:
            logger.error('GIS file helper is None')
            return False        
            
        if not ScratchDirectoryHelper._does_scratch_work_directory_exist(gis_data_file):
            return True
        
        try:
            shutil.rmtree(gis_data_file.gis_scratch_work_directory)
            return True
        except:
            logger.error('Failed to delete directory: %s:' % gis_data_file.gis_scratch_work_directory) 
            return False
    
    @staticmethod
    def get_scratch_work_directory(gis_data_file):
        """Ensure that the scratch work directory exists
        Success - return the full path to the directory
        Fail - return None
        """
        if gis_data_file is None:
            return None
        
        # If directory exists, return it
        if ScratchDirectoryHelper._does_scratch_work_directory_exist(gis_data_file):
            return gis_data_file.gis_scratch_work_directory
            
        # If directory doesn't exist, create it
        if ScratchDirectoryHelper._make_scratch_work_directory(gis_data_file):
            return gis_data_file.gis_scratch_work_directory
        
        return None
    
    @staticmethod
    def _does_scratch_work_directory_exist(gis_data_file):
        """Check the attribute gis_scratch_work_directory:
            - Is it populated?
            - Does it contain a valid directory?
        """
        if gis_data_file is None:
            return False
            
        if gis_data_file.gis_scratch_work_directory and \
            os.path.isdir(gis_data_file.gis_scratch_work_directory):
            return True
        return False
         
         
    @staticmethod
    def _make_scratch_work_directory(gis_data_file):
        """For a GISDataFile object, create a scratch directory.
        Added to the base specified by the settings.GISFILE_SCRATCH_WORK_DIRECTORY 
        Assumes that directory doesn't exist, 
        Returns True or False
        """
        if gis_data_file is None:
            return False
        
        if not gis_data_file.id:
            gis_data_file.save()  # save to create id
            
        dirname = os.path.join(settings.GISFILE_SCRATCH_WORK_DIRECTORY\
                                , '%s__%s' % (datetime.today().strftime(ScratchDirectoryHelper.TIME_FORMAT_STRING)\
                                                , gis_data_file.id)\
                                )
        
        if os.path.isdir(dirname):
            return True 
            
        try:
            os.makedirs(dirname)
            gis_data_file.gis_scratch_work_directory = dirname
            gis_data_file.save()
            return True
        except:
            logger.critical('Failed to create directory: %s:' % dirname) 
            return False


    