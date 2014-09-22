import os
from hashlib import md5

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.db import models

from apps.core.models import TimeStampedModel

from apps.gis_basic_file.models import GISDataFile
from geo_utils.fsize_human_readable import sizeof_fmt
from geo_utils.json_field_reader import JSONFieldReader


class GISExcelFile(GISDataFile):
    """Expects an xls or xlsx file
    - With user input, choose geography
    """
    name = models.CharField(max_length=255, blank=True)        #   shapefile basename

    file_checked = models.BooleanField(default=False)
    number_of_features = models.IntegerField(default=0)

    bounding_box = models.CharField(max_length=255, blank=True)
    column_names = models.TextField(blank=True, help_text='Saved as a json list')
    geo_columns = models.TextField(blank=True, help_text='Saved as a json list')
    extracted_shapefile_load_path = models.CharField(blank=True, max_length=255, help_text='Used to load extracted shapfile set')
    
    
    def add_bounding_box(self, l=[]):
        print 'really add_bounding_box', l
        print 'json string', JSONFieldReader.get_python_val_as_json_string(l)
        self.bounding_box = JSONFieldReader.get_python_val_as_json_string(l)

    def get_bounding_box(self):
        return JSONFieldReader.get_json_string_as_python_val(self.bounding_box)

    
    def get_column_count(self):
        cols = self.get_column_names()
        if cols:
            return len(cols)
    

    def add_column_names(self, l=[]):
        if l is None:
            return 

        if not type(l) in (list, tuple):
            return
        self.column_names = JSONFieldReader.get_python_val_as_json_string(l)

    def get_column_names(self):
        return JSONFieldReader.get_json_string_as_python_val(self.column_names)

    #def add_column_info(self, l=[]):
    # Character, Numbers, Longs, Dates, or Memo. 
    #    self.column_info = JSONFieldReader.get_python_val_as_json_string(l)

    #def get_column_info(self):
    #    return JSONFieldReader.get_json_string_as_python_val(self.column_info)
       
    def get_basename(self):
        return os.path.basename(self.name)
        
    def save(self, *args, **kwargs):
        if not self.id:
            super(ShapefileInfo, self).save(*args, **kwargs)
        self.md5 = md5('%s%s' % (self.id, self.name)).hexdigest()

        super(ShapefileInfo, self).save(*args, **kwargs)
    
    def __unicode__(self):
        if self.name:
            return self.name
        return super(GISExcelFile, self).__unicode__()

    class Meta:
        ordering = ('-modified', 'datafile_label')
        #unique_together = ('name', 'shapefile_group')
