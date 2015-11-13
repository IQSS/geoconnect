import os
from hashlib import md5
from django.utils.text import slugify
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.db import models
from jsonfield import JSONField

from apps.core.models import TimeStampedModel

from apps.gis_basic_file.models import GISDataFile, dv_file_system_storage
from geo_utils.json_field_reader import JSONFieldReader

SHAPEFILE_MANDATORY_EXTENSIONS = ['.shp', '.shx', '.dbf',]
WORLDMAP_MANDATORY_IMPORT_EXTENSIONS =  SHAPEFILE_MANDATORY_EXTENSIONS + ['.prj']   # '.prj' required for WorldMap shapefile ingest

class GeoType(models.Model):
    """Information may be updated via the WorldMap JoinTypes API"""
    name = models.CharField(max_length=255)
    sort_order = models.IntegerField(default=10)
    description = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(max_length=255, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(name)
        super(GeoType, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('sort_order', 'name')

class SimpleTabularTest(TimeStampedModel):

    name = models.CharField(max_length=255, blank=True)        #   file basename

    dv_file = models.FileField(upload_to='tab_files/%Y/%m/%d', blank=True, null=True, storage=dv_file_system_storage)

    delimiter = models.CharField(max_length=10, default="\t")

    is_file_readable = models.BooleanField(default=False)

    num_rows = models.IntegerField(default=0)
    num_columns = models.IntegerField(default=0)

    column_names = JSONField(blank=True, help_text='Saved as a json list')
    #column_info = models.TextField(blank=True, help_text='Includes column type, field length, and decimal length. Saved as a json list.')

    # User mediated choices
    has_header_row = models.BooleanField(default=True)
    chosen_column = models.CharField(max_length=155, blank=True)
    chosen_column_type = models.ForeignKey(GeoType, blank=True, null=True, on_delete=models.PROTECT)

    def __str__(self):
        return self.name

    def test_page(self):
        if not self.id:
            return 'n/a'
        lnk = reverse('view_test_1', kwargs=dict(tabular_id=self.id))
        return '<a href="%s" target="_blank">test page</a>' % lnk
    test_page.allow_tags=True

    class Meta:
        verbose_name = 'GIS Simple Tabular (for dev)'
        verbose_name_plural = verbose_name


class TabularFileInfo(GISDataFile):
    """
    Tabular File Information.
    """
    name = models.CharField(max_length=255, blank=True)        #   file basename

    delimiter = models.CharField(max_length=10, default=",")

    is_file_readable = models.BooleanField(default=False)

    num_rows = models.IntegerField(default=0)
    num_columns = models.IntegerField(default=0)

    column_names = JSONField(blank=True, help_text='Saved as a json list')
    #column_info = models.TextField(blank=True, help_text='Includes column type, field length, and decimal length. Saved as a json list.')

    # User mediated choices
    has_header_row = models.BooleanField(default=True)
    chosen_column = models.CharField(max_length=155, blank=True)
    chosen_column_type = models.ForeignKey(GeoType, blank=True, null=True, on_delete=models.PROTECT)


    def get_column_count(self):
        cols = self.get_column_names()
        if cols:
            return len(cols)

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
        self.column_names = JSONFieldReader.get_python_val_as_json_string(l)

    def get_column_names(self):
        return JSONFieldReader.get_json_string_as_python_val(self.column_names)

    def add_column_info(self, l=[]):
        # Character, Numbers, Longs, Dates, or Memo.
        self.column_info = JSONFieldReader.get_python_val_as_json_string(l)

    def get_column_info(self):
        return JSONFieldReader.get_json_string_as_python_val(self.column_info)

    def save(self, *args, **kwargs):
        if not self.id:
            super(TabularFileInfo, self).save(*args, **kwargs)
        self.md5 = md5('%s%s' % (self.id, self.name)).hexdigest()

        super(TabularFileInfo, self).save(*args, **kwargs)

    def __unicode__(self):
        if self.name:
            return self.name
        return super(TabularFileInfo, self).__unicode__()

    class Meta:
        ordering = ('-modified', 'datafile_label')
        verbose_name = 'Tabular File Information'
        verbose_name_plural = verbose_name
