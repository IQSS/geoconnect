"""Abstract model describing WorldMap Layers"""
from abc import abstractmethod
from urlparse import urlparse
import logging

from django.conf import settings
from django.db import models
from django import forms

import jsonfield  # using jsonfield.JSONField

from shared_dataverse_information.dataverse_info.forms_existing_layer\
    import CheckForExistingLayerForm

from shared_dataverse_information.map_layer_metadata.forms import\
    MapLayerMetadataValidationForm,\
    GeoconnectToDataverseMapLayerMetadataValidationForm,\
    GeoconnectToDataverseDeleteMapLayerMetadataForm

from .download_link_formatter import DownloadLinkFormatter

from gc_apps.core.models import TimeStampedModel
from gc_apps.geo_utils.json_field_reader import JSONHelper

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
        """model meta info"""
        abstract = True
        ordering = ('-modified', '-created')
        verbose_name = 'WorldMapLayerInfo'
        verbose_name_plural = verbose_name


    def __str__(self):
        """string representation"""
        return self.layer_name

    @abstractmethod
    def get_layer_type(self):
        """return type such as:
        TYPE_JOIN_LAYER, TYPE_LAT_LNG_LAYER, TYPE_SHAPEFILE_LAYER, etc"""

    @abstractmethod
    def get_gis_data_info(self):
        """Return the attribute holding gis_data_file
        e.g. return self.tabular_info
        OR   return self.shapefile_info, etc"""

    @abstractmethod
    def get_description_for_core_data(self):
        """Return a description of the map layer source.
        e.g. 'Layer created from tabular file'"""

    @abstractmethod
    def get_failed_rows(self):
        """Return a list of rows which failed to map.
        e.g. 'Layer created from tabular file'"""

    def is_shapefile_layer(self):
        """Is this the result of mapping a zipped shapefile?"""
        return False
        #self.get_layer_type() == DV_MAP_TYPE_SHAPEFILE

    def is_lat_lng_layer(self):
        """Is this the result of mapping Lat/Lng columns?"""
        return False
        #return self.get_layer_type() == TYPE_LAT_LNG_LAYER

    def is_join_layer(self):
        """Is this the result of joining an existing layer?"""
        return False
        #return self.get_layer_type() == TYPE_JOIN_LAYER


    def get_core_data_dict_for_views(self):
        """
        Parameters used for HTML views of map data:
            core_data, attribute_data, download_links
        """
        return dict(worldmap_layerinfo=self,
                    core_data=self.core_data,
                    attribute_data=self.attribute_data,
                    download_links=self.get_formatted_download_links())

    def get_dict_for_classify_form(self):
        """
        Parameters used for populating the classification form
        # Override in concrete class
        """
        return dict(layer_name=self.layer_name,\
                data_source_type=self.get_layer_type(),\
                raw_attribute_info=self.attribute_data)


    def get_download_link(self, link_type='png'):
        """
        See download_link_formatter.DownloadLinkFormatter
        for different format types
        """
        if not self.download_links:
            return None

        return self.download_links.get('png', None)


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
            LOGGER.error(('Failed to convert core_data'
                          ' "attribute_info" from string'
                          ' to python object (list)'))
            return None

        # -----------------------------------------
        # Get download_links (optional)
        # Note: Currently this is an escaped string within core data...
        # -----------------------------------------
        if 'download_links' in core_data:
            download_links = JSONHelper.to_python_or_none(core_data['download_links'])

            if download_links is None:
                LOGGER.error(('Failed to convert core_data "download_links"'
                              ' from string to python object (list)'))
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
    def clear_duplicate_worldmapinfo(worldmap_info):
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

        if worldmap_info.is_shapefile_layer():
            filters = dict(shapefile_info=worldmap_info.get_gis_data_info(),\
                layer_name=worldmap_info.layer_name)
        else:
            filters = dict(tabular_info=worldmap_info.get_gis_data_info(),\
                        layer_name=worldmap_info.layer_name)

        # Pull objects except the current "worldmap_info"
        #
        older_info_objects = WorldMapLayerInfoType.objects\
                                .filter(**filters)\
                                .exclude(id=worldmap_info.id)

        # Delete the older objects
        older_info_objects.delete()


    def get_layer_url_base(self):
        """
        Return the layer url base. Examples:
            - http://worldmap.harvard.edu
            - http(s)://worldmap.harvard.edu
        """
        if not self.core_data:
            return None

        layer_link = self.core_data.get('layer_link', None)
        if layer_link is None:
            return None

        parsed_url = urlparse(layer_link)

        return '%s://%s' % (parsed_url.scheme, parsed_url.netloc)


    def get_params_to_check_for_existing_layer_metadata(self):
        """Return dict of params used to check WorldMap
        for existing layer metadata"""

        gis_data_info = self.get_gis_data_info()
        assert gis_data_info is not None, "gis_data_info cannot be None"

        f = CheckForExistingLayerForm(gis_data_info.__dict__)
        if not f.is_valid():
            raise forms.ValidationError(\
                'CheckForExistingLayerForm params did not validate: %s'\
                 % f.errors)

        return f.cleaned_data

    def get_params_for_dv_delete_layer_metadata(self):
        """Return dict of params used to delete an
        WorldMap metadata from Dataverse"""

        gis_data_info = self.get_gis_data_info()
        assert gis_data_info is not None, "gis_data_info cannot be None"

        f = GeoconnectToDataverseDeleteMapLayerMetadataForm(\
                {'dv_session_token' : gis_data_info.dv_session_token})

        if not f.is_valid():
            raise forms.ValidationError(\
                'WorldMapLayerInfo DELETE params did not validate: %s' %\
                 f.errors)

        return f.format_for_dataverse_api()


    def get_legend_img_url(self, force_https=False):
        """
        Construct a url that returns a Legend for a Worldmap layer in the form of PNG file
        """
        if not self.core_data:
            return None

        params = (('request', 'GetLegendGraphic')\
                   , ('format', 'image/png')\
                   , ('width', 20)\
                   , ('height', 20)\
                   , ('layer', self.layer_name)\
                   , ('legend_options', 'fontAntiAliasing:true;fontSize:11;')\
                )
        param_str = '&'.join(['%s=%s' % (k, v) for k, v in params])

        legend_img_url = '%s/geoserver/wms?%s' %\
                                (self.get_layer_url_base(),
                                 param_str)
        if force_https:
            return legend_img_url.replace('http://', 'https://', 1)
        else:
            return legend_img_url

        """
        Example of how an image tag is formed:
        <img src="{{ worldmap_layerinfo.get_layer_url_base }}
        /geoserver/wms?request=GetLegendGraphic&format=image/png&width=20&height=20
        &layer={{ worldmap_layerinfo.layer_name }}
        &legend_options=fontAntiAliasing:true;fontSize:12;
        &trefresh={% now "U" %}" id="legend_img" alt="legend" />
        """

    def get_dataverse_server_url(self):
        """
        Retrieve the Dataverse base url to be used
        for using the Dataverse API
        """
        wm_info = self.get_gis_data_info()

        if not wm_info:
            return None

        return wm_info.get_dataverse_server_url()

    def get_data_dict(self, json_format=False):
        """
        Used for processing model data.
        """
        f = MapLayerMetadataValidationForm(self.core_data)
        if not f.is_valid():
            raise forms.ValidationError('WorldMapLayerInfo params did not validate: %s' % f.errors)

        if not json_format:
            return f.cleaned_data

        try:
            return json.dumps(f.cleaned_data)
        except:
            raise ValueError('Failed to convert data to json\ndata: %s' % f.cleaned_data)


    def get_layer_link(self):

        if not self.core_data:
            return None

        layer_link = self.core_data.get('layer_link', None)
        if not layer_link:
            return None

        if layer_link.startswith('/'):
            return settings.WORLDMAP_SERVER_URL + layer_link

        return layer_link

    def get_params_for_dv_update(self):
        """
        Format data to send to the Dataverse
        """
        self.verify_layer_link_format()
        if self.core_data and self.core_data.get('joinDescription') is None:
            self.core_data['joinDescription'] = self.get_description_for_core_data()
            self.save()

        f = GeoconnectToDataverseMapLayerMetadataValidationForm(self.core_data)
        if not f.is_valid():
            raise forms.ValidationError('WorldMapLayerInfo params did not validate: %s' % f.errors)

        gis_data_info = self.get_gis_data_info()
        if gis_data_info is None:
            raise forms.ValidationError(\
                'Serious error!  Could not find gis_data_info: %s' % f.errors)

        return f.format_data_for_dataverse_api(gis_data_info.dv_session_token,\
                        join_description=self.get_description_for_core_data())


    def get_formatted_download_links(self):
        """Format the download links from WorldMap"""
        if not self.download_links:
            return None

        dl = DownloadLinkFormatter(self.download_links)

        return dl.get_formatted_links()



    def get_embed_map_link(self, force_https=False):
        """
        Return the WorldMap embed link.
        By default, make the link 'https'
        """
        if not self.core_data:
            return None

        embed_link = self.core_data.get('embed_map_link', None)
        if not embed_link:
            return None

        if force_https and embed_link.startswith('http://'):
            return embed_link.replace('http://', 'https://', 1)

        return embed_link


    def verify_layer_link_format(self):
        """
        Hack to make sure the layer_link is a full url and not just the path

        e.g., If it's just the path, take the rest of the url from the embed_link
        """
        layer_link = self.core_data.get('layer_link', None)

        # Is it just a path?
        if layer_link and layer_link.startswith('/'):
            full_link = self.core_data.get('embed_link', None)
            if not full_link:
                full_link = self.core_data.get('map_image_link', None)

            # Does the embed link a full url
            if full_link and full_link.lower().startswith('http'):
                # Parse the embed link and use it to reformat the layer_link
                url_parts = urlparse(full_link)

                # Full layer link
                layer_link = '%s://%s%s' % (url_parts.scheme,
                                            url_parts.netloc,
                                            layer_link)
                self.core_data['layer_link'] = layer_link
                self.save()
