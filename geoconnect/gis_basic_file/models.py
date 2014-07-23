from hashlib import md5
from datetime import date

from os.path import basename, isfile

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.db import models
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from core.models import TimeStampedModel

from gis_basic_file.scratch_directory_services import ScratchDirectoryHelper

dv_file_system_storage = FileSystemStorage(location=settings.DV_DATAFILE_DIRECTORY)

class GISDataFile(TimeStampedModel):
    """GeoConnect - For working with a Dataverse File for a given user
    These objects will persist for a limited time (days, weeks), depending on the system demand
    """
    # Dataverse user info
    dv_user_id = models.IntegerField()          # for API calls
    dv_user_email = models.EmailField(default='raman_prasad@harvard.edu')          # for API calls
    dv_username = models.CharField(max_length=255)  # for display

    # DataFile
    datafile_id = models.IntegerField()  # for API calls.  dvobject.id; dtype='DataFile'
    #datafile_version = models.BigIntegerField()
    datafile_label = models.CharField(max_length=255, blank=True)    # for display; filemetadata.label   (dvobject.id = filemetadata.datafile_id)

    # Copy of the actual file
    dv_file = models.FileField(upload_to='dv_files/%Y/%m/%d', blank=True, null=True, storage=dv_file_system_storage)

    datafile_description = models.TextField(blank=True)    # for display; filemetadata.description   (dvobject.id = filemetadata.datafile_id)
    datafile_type = models.CharField(max_length=255, help_text='Usually mime type')    # dvobject.contenttype
    datafile_expected_md5_checksum = models.CharField(blank=True, max_length=255)    # dvobject.md5
   
    # Owning dataverse
    dv_id = models.IntegerField(default=-1)       # for API calls.  dvobject.id; dtype='Dataverse'
    dv_name = models.CharField(max_length=255, blank=True)  # for display
    
    # Dataset Info
    dataset_id = models.IntegerField(default=-1)  # for API calls.  dvobject.id; dtype='Dataset'

    dataset_version_id = models.IntegerField(default=-1)  # for API calls.  dvobject.id; dtype='Dataset'
    dataset_name = models.CharField(max_length=255, blank=True)  # for display
    dataset_description = models.TextField(blank=True) # for display

   
    
    # session token
    # Token used to make requests of the Dataverse api; may expire, be refreshed
    dv_session_token = models.CharField(max_length=255, blank=True)
    

    # For file working.  examples: unzipping, pulling raw data from columns, etc
    gis_scratch_work_directory = models.CharField(max_length=255, blank=True, help_text='scratch directory for files')
    
    # for object identifcation
    md5 = models.CharField(max_length=40, blank=True, db_index=True, help_text='auto-filled on save')
  
    
    def is_dv_file_available(self):
        """Does the file actually exist in the dv_file specified path"""
        
        if isfile(self.get_dv_file_fullpath):
            return True
        return False

    def get_dv_file_basename(self):
        if not self.dv_file:
            return None
            
        return basename(self.dv_file.name)
    
    def get_dv_file_fullpath(self):
        if not self.dv_file:
            return None
            
        return self.dv_file.file.name
        
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

        self.md5 = md5('%s%s%s' % (self.id, self.dv_user_id, self.datafile_id)).hexdigest()
        super(GISDataFile, self).save(*args, **kwargs)


    def __unicode__(self):
        if self.dv_name and self.dataset_name and self.datafile_label:
            return '%s : %s : %s' % (self.dv_name, self.dataset_name, self.datafile_label)
        return '%s %s' % (self.datafile_id, self.dv_user_id)
        return self.id  # shouldn't happen

    class Meta:
        ordering = ('-modified',  )
        
'''
class GISDataFile(TimeStampedModel):
    """Superclass for a GIS File "Helper"
    - Examples of GIS files: shapefiles, GeoTiffs, spreadsheets or delimited text files with lat/lng, GeoJSON etc
    """
    name = models.CharField(max_length=255, help_text='For testing.  Should be auto-fill metadata')

    dv_username = models.CharField(max_length=100, blank=True)

    dataset_name = models.CharField(max_length=255, help_text='auto-filled on save', blank=True)
    dataset_link = models.URLField(max_length=255, help_text='auto-filled on save', blank=True)
    dataset_description = models.CharField(max_length=255, help_text='auto-filled on save', blank=True)
    
    gis_file_type = models.CharField(blank=True, max_length=255, help_text='auto-filled on save', db_index=True)

    gis_scratch_work_directory = models.CharField(max_length=255, blank=True, help_text='scratch directory for files')
    
    md5 = models.CharField(max_length=40, blank=True, db_index=True, help_text='auto-filled on save')
    
    
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
        
    def test_view(self):
        if not self.gis_file_type:
            return None
            
        if hasattr(self, self.gis_file_type.lower()):
            subclass = eval('self.%s' % self.gis_file_type.lower())
            if subclass is not None:
                return subclass.test_view()
        return None
        
        #return '<a href="%s">test view</a>' % ('http://127.0.0.1:8000/shp-test/view-shp/' + self.md5)    
    test_view.allow_tags = True
    
    def get_absolute_url(self):
        if not self.gis_file_type:
            return None
            
        if hasattr(self, self.gis_file_type.lower()):
            subclass = self.__dict__.get('gis_file_type')
            if subclass is not None:
                return subclass.get_absolute_url()
        return None
                                
        
    def save(self, *args, **kwargs):
        if not self.id:
            super(GISDataFile, self).save(*args, **kwargs)
        
        self.md5 = md5('%s%s' % (self.id, self.name)).hexdigest()
        super(GISDataFile, self).save(*args, **kwargs)
        
        
    def __unicode__(self):
        return self.name
        
        
    class Meta:
        ordering = ('-modified',  )
        #verbose_name = 'COA File Load Log'
'''