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

    def get_file_info(self):
        return self.singlefileinfo_set.all()

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


    def get_shp_fileinfo_obj(self):
        l = SingleFileInfo.objects.filter(shapefile_info=self, extension='.shp')
        cnt = l.count()
        if cnt == 0:
            return None
        elif cnt == 1:
            return l[0]
        # cnt > 1
        selected_info = l[0]
        SingleFileInfo.objects.exclude(id=l[0].id).filter(shapefile_info=self, extension='.shp').delete()  # delete others

        return selected_info

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


class SingleFileInfo(TimeStampedModel):
    """
    For a shapefile set, this is metadata on the individual files.
    """
    name = models.CharField(max_length=255)
    shapefile_info = models.ForeignKey(ShapefileInfo)
    extension= models.CharField(max_length=40, blank=True, help_text='auto-filled on save')
    filesize = models.IntegerField(help_text='in bytes')
    is_required_shapefile = models.BooleanField(default=False, help_text='auto-filled on save')

    extracted_file_path = models.CharField(max_length=255, blank=True)

    md5 = models.CharField(max_length=40, blank=True, db_index=True, help_text='auto-filled on save')

    def get_human_readable_filesize(self):
        """Get human readable filesize, e.g. 13.7 MB"""
        return sizeof_fmt(self.filesize)

    def filesize_text(self):
        """Display human readable filesize in the admin"""
        return self.get_human_readable_filesize()
    filesize_text.allow_tags=True

    def save(self, *args, **kwargs):
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
        ordering = ('-modified', 'name')
        verbose_name = 'Single File Information'
        verbose_name_plural = verbose_name
