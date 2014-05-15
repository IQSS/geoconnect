from hashlib import md5
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.db import models
from datetime import date
from gis_basic_file.scratch_directory_services import ScratchDirectoryHelper
import shutil

class GISFileHelper(models.Model):
    """Superclass for a GIS File "Helper"
    - Examples of GIS files: shapefiles, GeoTiffs, spreadsheets or delimited text files with lat/lng, GeoJSON etc
    """
    name = models.CharField(max_length=255, help_text='For testing.  Should be auto-fill metadata')

    dv_username = models.CharField(max_length=100, blank=True)

    dataset_name = models.CharField(max_length=255, help_text='auto-filled on save', blank=True)
    dataset_link = models.URLField(max_length=255, help_text='auto-filled on save', blank=True)
    dataset_citation = models.CharField(max_length=255, help_text='auto-filled on save', blank=True)
    
    gis_file_type = models.CharField(blank=True, max_length=255, help_text='auto-filled on save', db_index=True)

    gis_scratch_work_directory = models.CharField(max_length=255, blank=True, help_text='scratch directory for files')
    
    md5 = models.CharField(max_length=40, blank=True, db_index=True, help_text='auto-filled on save')
    
    update_time = models.DateTimeField(auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)
    
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
            super(GISFileHelper, self).save(*args, **kwargs)
        
        self.md5 = md5('%s%s' % (self.id, self.name)).hexdigest()
        super(GISFileHelper, self).save(*args, **kwargs)
        
        
    def __unicode__(self):
        return self.name
        
        
    class Meta:
        ordering = ('-update_time',  )
        #verbose_name = 'COA File Load Log'
