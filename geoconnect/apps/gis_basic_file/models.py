from hashlib import md5
from datetime import date

from django.template.loader import render_to_string

from os.path import basename, isfile

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.db import models
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from apps.core.models import TimeStampedModel

from apps.registered_dataverse.models import RegisteredDataverse
from shared_dataverse_information.dataverse_info.models import DataverseInfo
from apps.gis_basic_file.scratch_directory_services import ScratchDirectoryHelper

dv_file_system_storage = FileSystemStorage(location=settings.DV_DATAFILE_DIRECTORY)

class GISDataFile(DataverseInfo):
    """
    This object stores information describing a geospatial Dataverse File
    For continuity between GeoConnect and WorldMap, both project use the DataverseInfo model
    """
    
    #
    # RegisteredDataverse - Used for calls back to Dataverse API
    #
    registered_dataverse = models.ForeignKey(RegisteredDataverse)
    
    # session token
    # Token used to make requests of the Dataverse api; may expire, be refreshed
    #
    dv_session_token = models.CharField(max_length=255, blank=True)

    # Copy of the actual file
    dv_file = models.FileField(upload_to='dv_files/%Y/%m/%d', blank=True, null=True, storage=dv_file_system_storage)
    
    # For file working.  examples: unzipping, pulling raw data from columns, etc
    gis_scratch_work_directory = models.CharField(max_length=255, blank=True, help_text='scratch directory for files')

    # for object identification
    md5 = models.CharField(max_length=40, blank=True, db_index=True, help_text='auto-filled on save')
    

    def is_datafile_private(self):
        """Is the datafile private on Dataverse?

        return the opposite of "dataset_is_public"
        """
        return not self.dataset_is_public

    def get_dataverse_server_url(self):
        if not self.registered_dataverse:
            return None
            
        return self.registered_dataverse.dataverse_url
        

    def is_dv_file_available(self):
        """Does the file actually exist in the dv_file specified path"""
        fullpath = self.get_dv_file_fullpath()
        if fullpath is None:
            return False

        try:
            if isfile(fullpath):
                return True
        except IOError:
            return False

        return False

    def get_dv_file_basename(self):
        if not self.dv_file:
            return None
            
        return basename(self.dv_file.name)
    
    def get_dv_file_fullpath(self):
        if not self.dv_file:
            return None

        try:
            return self.dv_file.file.name
        except IOError:
            return None


    def get_scratch_work_directory(self):
        """Return the full path of the scratch working directory.  
        Creates directory if it doesn't exist """
        return ScratchDirectoryHelper.get_scratch_work_directory(self)

    def delete_scratch_work_directory(self):
        """Deletes the scratch working directory, if it exists"""
        return ScratchDirectoryHelper.delete_scratch_work_directory(self)

    def has_style_layer_information(self):
        if self.stylelayerinformation__set.count() > 0:
            return True
        return False

    def get_style_layer_information(self):
        l = self.stylelayerinformation_set.all()
        if len(l) == 0:
            return None
        return l
        
    def save(self, *args, **kwargs):
        if not self.id:
            super(GISDataFile, self).save(*args, **kwargs)

        self.md5 = md5('%s%s%s' % (self.id, self.datafile_id, self.dataverse_installation_name)).hexdigest()
        super(GISDataFile, self).save(*args, **kwargs)


    def get_abstract_for_worldmap(self):
        return render_to_string('gis_basic_file/worldmap_abstract.html', { 'gis_file' : self })
        

    def __unicode__(self):
        if self.dataverse_name and self.dataset_name and self.datafile_label:
            return '%s : %s : %s' % (self.dataverse_name, self.dataset_name, self.datafile_label)
        return '%s %s' % (self.datafile_id, self.dv_user_id)
        #return self.id  # shouldn't happen


    class Meta:
        ordering = ('-modified',  )

