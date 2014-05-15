import os
from hashlib import md5
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.db import models
from gis_basic_file.models import GISFileHelper
from dv_geo_utils.fsize_human_readable import sizeof_fmt
from dv_geo_utils.json_field_reader import JSONFieldReader
SHAPEFILE_MANDATORY_EXTENSIONS = ['.shp', '.shx', '.dbf',]
WORLDMAP_MANDATORY_IMPORT_EXTENSIONS =  SHAPEFILE_MANDATORY_EXTENSIONS + ['.prj']   # '.prj' required for WorldMap shapefile ingest

class ShapefileGroup(GISFileHelper):
    """Expects a .zip file upload
    Modify in the future for shapefiles loaded separately
    """
    shp_file = models.FileField(upload_to='shp_process', max_length=255)

    zipfile_checked = models.BooleanField(default=False)
    has_shapefile = models.BooleanField(default=False)
    
    shapefile_names = models.TextField(blank=True, help_text='saved as JSON')
    num_shapefiles = models.IntegerField(default=0)
    
    def add_shapefile_names(self, l=[]):
        self.shapefile_names = JSONFieldReader.get_python_val_as_json_string(l)
        
    def get_shapefile_names(self):
        return JSONFieldReader.get_json_string_as_python_val(self.shapefile_names)
        
        
    def get_shapefile_basenames(shapefile_names):
        l = self.get_shapefile_names()
        if l is None or len(l) == 0:
            return None

        return [os.path.basename(x) for x in l]
        
        
    def is_single_shapefile(self):
        if self.num_shapfiles == 1:
            return True
        return False
        
    def test_view(self):
        if not self.md5:
            return 'n/a'
        return '<a href="%s">test view</a>' % reverse('view_choose_shapefile', kwargs={ 'shp_md5' : self.md5 })
    test_view.allow_tags = True
    
    def get_absolute_url(self):
        return 'blah! (ShapefileGroup)'
                                
        
    def save(self, *args, **kwargs):
        self.gis_file_type = self.__class__.__name__        
        super(ShapefileGroup, self).save(*args, **kwargs)
 
    class Meta:
        ordering = ('-update_time',  )
        #verbose_name = 'COA File Load Log'

 
    
class SingleShapefileSet(models.Model):
    """Used for working with a selected shapefile, specifically using the extensions specified in WORLDMAP_MANDATORY_IMPORT_EXTENSIONS
    
    """
    name = models.CharField(max_length=255)        #   shapefile basename
    shapefile_group = models.ForeignKey(ShapefileGroup)
    number_of_features = models.IntegerField(default=0)
    bounding_box = models.CharField(max_length=255, blank=True)
    column_names = models.TextField(blank=True, help_text='Saved as a json list')
    extracted_shapefile_load_path = models.CharField(blank=True, max_length=255, help_text='Used to load extracted shapfile set')
    
    #has_required_files
    
    md5 = models.CharField(max_length=40, blank=True, db_index=True, help_text='auto-filled on save')
    
    update_time = models.DateTimeField(auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)
    
    def get_file_info(self):
        return self.singlefileinfo_set.all()
    
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
        self.column_names = JSONFieldReader.get_python_val_as_json_string(l)

    def get_column_names(self):
        return JSONFieldReader.get_json_string_as_python_val(self.column_names)
        
    def get_basename(self):
        return os.path.basename(self.name)
        
    def __save__(self, *args, **kwargs):
        if not self.id:
            super(SingleShapefileSet, self).save(*args, **kwargs)
        self.md5 = md5('%s%s' % (self.id, self.shapefile)).hexdigest()

        super(SingleShapefileSet, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('-update_time', 'name')
        unique_together = ('name', 'shapefile_group')


class SingleFileInfo(models.Model):
    """
    For a shapefile set, this is metadata on the individual files.
    """
    name = models.CharField(max_length=255)
    shapefile_set = models.ForeignKey(SingleShapefileSet)
    extension= models.CharField(max_length=40, blank=True, help_text='auto-filled on save')
    filesize = models.IntegerField(help_text='in bytes')
    is_required_shapefile = models.BooleanField(default=False, help_text='auto-filled on save')

    extracted_file_path = models.CharField(max_length=255, blank=True)

    md5 = models.CharField(max_length=40, blank=True, db_index=True, help_text='auto-filled on save')

    update_time = models.DateTimeField(auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)


    def get_human_readable_filesize(self):
        """Get human readable filesize, e.g. 13.7 MB"""
        return self.sizeof_fmt(self.filesize)

    def filesize_text(self):
        """Display human readable filesize in the admin"""
        return self.get_human_readable_filesize()
    filesize_text.allow_tags=True

    def __save__(self, *args, **kwargs):
        # Set file extension
        fparts = self.name.split('.')
        if len(fparts) > 1:
            self.extension = '.%s' % fparts[-1].lower()

        # Set is_mandatory_shapefile
        if self.extension in WORLDMAP_MANDATORY_IMPORT_EXTENSIONS:
            self.is_mandatory_shapefile = True
        else:
            self.is_mandatory_shapefile = False

        if not self.id:
            super(SingleFileInfo, self).save(*args, **kwargs)
        self.md5 = md5('%s%s' % (self.id, self.name)).hexdigest()

        super(SingleFileInfo, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('-update_time', 'name')
        verbose_name = 'Single File Information'
        verbose_name_plural = verbose_name
