"""Abstract model describing WorldMap Layers"""

from django.db import models
import jsonfield  # using jsonfield.JSONField

import logging

from apps.core.models import TimeStampedModel
from geo_utils.json_field_reader import JSONHelper

LOGGER = logging.getLogger(__name__)

class WorldMapLayerInfo(TimeStampedModel):
    """
    Store the results of a new layer created by mapping a Dataverse file
    Abstract model used as a mix-in
    """
    layer_name = models.CharField(max_length=255, blank=True, help_text='auto-filled on save')

    core_data = jsonfield.JSONField()
    attribute_data = jsonfield.JSONField()
    download_links = jsonfield.JSONField(blank=True)

    # for object identification
    md5 = models.CharField(max_length=40,\
                    blank=True,\
                    db_index=True,\
                    help_text='auto-filled on save')

    class Meta:
        abstract = True
        ordering = ('-created',)
        verbose_name = 'WorldMapLayerInfo'
        verbose_name_plural = verbose_name


    @staticmethod
    def build_dict_from_worldmap_json(json_dict):
        """Given json_dict containing WorldMap layer information,
        split out the core_data, attribute_data, and download_link information

        Used for creating subclass objects:
            - WorldMapShapefileLayerInfo
            - WorldMapJoinLayerInfo
            - WorldMapLatLngInfo
        """

        if json_dict is None:
            LOGGER.error('json_dict cannot be None')
            return None

        if not hasattr(json_dict, 'has_key'):
            LOGGER.error('json_dict must be a dict.  not type: [%s]', type(json_dict))
            return None

        # -----------------------------------------
        # Get core data (required)
        # -----------------------------------------
        if not 'data' in json_dict:
            LOGGER.error('The json_dict must have a "data" key')
            return None
        core_data = json_dict['data']

        # -----------------------------------------
        # Get attribute data (required)
        # Note: Currently this is an escaped string within core data...
        # -----------------------------------------
        if not 'attribute_info' in core_data:
            LOGGER.error('The core_data must have a "attribute_info" key')
            return None

        attribute_data = JSONHelper.to_python_or_none(core_data['attribute_info'])
        if attribute_data is None:
            LOGGER.error('Failed to convert core_data "attribute_info" from string to python object (list)')
            return None

        # -----------------------------------------
        # Get download_links (optional)
        # Note: Currently this is an escaped string within core data...
        # -----------------------------------------
        if 'download_links' in core_data:
            download_links =  JSONHelper.to_python_or_none(core_data['download_links'])

            if download_links is None:
                LOGGER.error('Failed to convert core_data "download_links" from string to python object (list)')
                download_links = ''
        else:
            download_links = ''

        # -----------------------------------------
        # Gather initial values
        # -----------------------------------------
        init_data = dict(core_data=core_data,\
                    attribute_data=attribute_data,\
                    download_links=download_links)

        return init_data


    @staticmethod
    def clear_duplicate_worldmap_info_objects(worldmap_info):
        """
        Remove any duplicate objects of the same subclass.
        Subclass objects include:
            - WorldMapShapefileLayerInfo
            - WorldMapJoinLayerInfo
            - WorldMapLatLngInfo

        worldmap_info - instance of a subclass above
        """
        if worldmap_info is None or not worldmap_info.id:
            # Make sure the object has been saved -- e.g. has an 'id'
            return

        assert isinstance(worldmap_info, WorldMapLayerInfo),\
            ("worldmap_info must be an instance/subclass of"
            " WorldMapJoinLayerInfo")

        WorldMapLayerInfoType = worldmap_info.__class__

        if hasattr(WorldMapLayerInfoType,'shapefile_info'):
            filters = dict(shapefile_info=worldmap_info.shapefile_info,\
                        layer_name=worldmap_info.layer_name)
        else:
            filters = dict(tabular_info=worldmap_info.tabular_info,\
                        layer_name=worldmap_info.layer_name)

        # Delete similar objects - same tabular file + same WorldMap layer
        # Bit of a hack due to fuzzy requirements early on
        # whether a tab file can have more than one map
        #

        # Pull objects except the current "worldmap_info"
        #
        older_info_objects = WorldMapLayerInfoType.objects\
                                .filter(**filters)\
                                .exclude(id=worldmap_info.id)

        # Delete the older objects
        older_info_objects.delete()
