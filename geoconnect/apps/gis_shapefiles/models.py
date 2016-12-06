import os
from hashlib import md5

from django.db import models

import jsonfield # jsonfield.JSONField

from apps.core.models import TimeStampedModel
from apps.gis_basic_file.models import GISDataFile
from geo_utils.fsize_human_readable import sizeof_fmt

SHAPEFILE_EXTENSION_SHP = '.shp'
SHAPEFILE_MANDATORY_EXTENSIONS = [SHAPEFILE_EXTENSION_SHP, '.shx', '.dbf',]
WORLDMAP_MANDATORY_IMPORT_EXTENSIONS =  SHAPEFILE_MANDATORY_EXTENSIONS + ['.prj']   # '.prj' required for WorldMap shapefile ingest

class ShapefileInfo(GISDataFile):
    """Expects a .zip file upload
    Modify in the future for shapefiles loaded separately
    """
    name = models.CharField(max_length=255, blank=True)        #   shapefile basename

    zipfile_checked = models.BooleanField(default=False)
    has_shapefile = models.BooleanField(default=False)
    #has_mulitple_shapefile

    number_of_features = models.IntegerField(default=0)
    bounding_box = models.CharField(max_length=255, blank=True)

    column_names = jsonfield.JSONField(blank=True, help_text='Saved as a json list')
    column_info = jsonfield.JSONField(blank=True, help_text='Includes column type, field length, and decimal length. Saved as a json list.')
    extracted_shapefile_load_path = models.CharField(blank=True, max_length=255, help_text='Used to load extracted shapfile set')
    #file_names = jsonfield.JSONField(blank=True, help_text='Files within the .zip')

    #def get_file_info(self):
    #    return self.file_names

    def add_bounding_box(self, l=[]):
        self.bounding_box = l

    def get_column_count(self):
        if not self.column_names:
            return 0
        else:
            return len(self.column_names)

    def add_column_names_using_fields(self, shp_reader_fields):
        if shp_reader_fields is None:
            return

        try:
            fields = shp_reader_fields[1:]
            field_names = [field[0] for field in fields]
            self.add_column_names(field_names)
        except:
            return

    def add_column_names(self, l=[]):
        """Set column names attribute"""
        self.column_names = l


    def add_column_info(self, l=[]):
        # Character, Numbers, Longs, Dates, or Memo.
        self.column_info = l

    def get_basename(self):
        return os.path.basename(self.name)

    def save(self, *args, **kwargs):
        if not self.id:
            super(ShapefileInfo, self).save(*args, **kwargs)
        #self.md5 = md5('%s%s' % (self.id, self.name, self.dataverse_instal)).hexdigest()
        self.md5 = md5('%s%s%s' % (self.id, self.datafile_id, self.dataverse_installation_name)).hexdigest()

        super(ShapefileInfo, self).save(*args, **kwargs)

    def __unicode__(self):
        if self.name:
            return self.name
        return super(ShapefileInfo, self).__unicode__()

    class Meta:
        ordering = ('-modified', 'datafile_label')
        #unique_together = ('name', 'shapefile_group')
        verbose_name = 'Shapefile Information'
        verbose_name_plural = 'Shapefile Information'
