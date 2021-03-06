import os
from hashlib import md5
import logging

from django.db import models

import jsonfield # jsonfield.JSONField

from gc_apps.core.models import TimeStampedModel
from gc_apps.gis_basic_file.models import GISDataFile
from gc_apps.geo_utils.fsize_human_readable import sizeof_fmt
from gc_apps.geo_utils.json_field_reader import JSONHelper
from gc_apps.layer_types.static_vals import TYPE_SHAPEFILE_LAYER
from gc_apps.worldmap_layers.models import WorldMapLayerInfo

SHAPEFILE_EXTENSION_SHP = '.shp'
SHAPEFILE_MANDATORY_EXTENSIONS = [SHAPEFILE_EXTENSION_SHP, '.shx', '.dbf',]
WORLDMAP_MANDATORY_IMPORT_EXTENSIONS =  SHAPEFILE_MANDATORY_EXTENSIONS + ['.prj']   # '.prj' required for WorldMap shapefile ingest

LOGGER = logging.getLogger(__name__)


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
    extracted_shapefile_load_path = models.CharField(blank=True, max_length=255, help_text='Used to load extracted shapefile set')
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
        self.md5 = md5('%s%s%s' % (\
                       self.id,
                       self.datafile_id,
                       self.dataverse_installation_name)).hexdigest()

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



class WorldMapShapefileLayerInfo(WorldMapLayerInfo):
    """
    Store the results of a new layer created by mapping a shapefile
    """
    shapefile_info = models.ForeignKey(ShapefileInfo)

    def save(self, *args, **kwargs):
        """When saving, set layer_name and md5"""

        if not self.id:
            super(WorldMapShapefileLayerInfo, self).save(*args, **kwargs)

        self.layer_name = self.core_data.get('layer_typename', None)
        if self.layer_name is None:
            self.layer_name = self.core_data.get('layer_name')

        self.md5 = md5('%s-%s' % (self.id, self.layer_name)).hexdigest()
        super(WorldMapShapefileLayerInfo, self).save(*args, **kwargs)


    class Meta:
        ordering = ('-created',)
        verbose_name = 'WorldMapShapefileLayerInfo'
        verbose_name_plural = verbose_name

    def get_layer_type(self):
        return TYPE_SHAPEFILE_LAYER

    def is_shapefile_layer(self):
        return True

    def get_gis_data_info(self):
        """Return the attribute holding gis_data_file"""
        return self.shapefile_info

    def get_description_for_core_data(self):
        """Define this depending on the subclass"""

        return 'Layer created my mapping a zipped Shapefile.'

    def get_failed_rows(self):
        """Not applicable to shapefiles"""
        return None

    def get_unmapped_record_count(self):
        """Not applicable to shapefiles"""
        return -1

    @staticmethod
    def build_from_worldmap_json(shapefile_info, json_dict):
        """
        Create WorldMapTabularLayerInfo object using
        a python dictionary containing information
        returned from the WorldMapLayerInfo.

        (Also used to for formatting when checking if a layer exists)
        """
        if not isinstance(shapefile_info, ShapefileInfo):
            LOGGER.error('shapefile_info must be a ShapefileInfo object')
            return None

        if json_dict is None:
            LOGGER.error('json_dict cannot be None')
            return None

        init_data = WorldMapLayerInfo.build_dict_from_worldmap_json(json_dict)
        if init_data is None:
            LOGGER.error('Failed to build WorldMapLayerInfo from WorldMap JSON: %s', json_dict)
            return None

        init_data['shapefile_info'] = shapefile_info

        # Create the object
        wm_info = WorldMapShapefileLayerInfo(**init_data)

        # Save it
        wm_info.save()

        # Clear dupe layers, if any
        WorldMapLayerInfo.clear_duplicate_worldmapinfo(wm_info)

        return wm_info
