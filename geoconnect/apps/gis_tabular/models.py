"""
Models to save the Tabular information from Dataverse
as well as the mapping results from WorldMap
"""
import json
from hashlib import md5
from urlparse import urlparse

import jsonfield  # using jsonfield.JSONField

from django.db import models
from django import forms

from shared_dataverse_information.dataverse_info.forms_existing_layer import CheckForExistingLayerForm
from shared_dataverse_information.map_layer_metadata.forms import\
    GeoconnectToDataverseMapLayerMetadataValidationForm,\
    GeoconnectToDataverseDeleteMapLayerMetadataForm

from apps.core.models import TimeStampedModel
from apps.gis_basic_file.models import GISDataFile, dv_file_system_storage
from apps.layer_types.static_vals import TYPE_JOIN_LAYER, TYPE_LAT_LNG_LAYER


#MapLayerMetadataValidationForm


SHAPEFILE_MANDATORY_EXTENSIONS = ['.shp', '.shx', '.dbf',]
WORLDMAP_MANDATORY_IMPORT_EXTENSIONS = SHAPEFILE_MANDATORY_EXTENSIONS\
    + ['.prj']   # '.prj' required for WorldMap shapefile ingest

import logging
LOGGER = logging.getLogger(__name__)

DEFAULT_TABULAR_DELIMITER = '\t'

class TabularFileInfo(GISDataFile):
    """
    Tabular File Information.
    """
    name = models.CharField(max_length=255, blank=True)        #   file basename

    delimiter = models.CharField(max_length=10, default=DEFAULT_TABULAR_DELIMITER)

    is_file_readable = models.BooleanField(default=False)

    num_rows = models.IntegerField(default=0)
    num_columns = models.IntegerField(default=0)

    column_names = jsonfield.JSONField(blank=True, help_text='Saved as a json list')

    # User mediated choices
    has_header_row = models.BooleanField(default=True)
    chosen_column = models.CharField(max_length=155, blank=True)

    dv_join_file = models.FileField(upload_to='dv_files/join/%Y/%m/%d',\
                blank=True, null=True,\
                storage=dv_file_system_storage,\
                max_length=255,\
                help_text="Used when a new column needs to be added for a TableJoin")

    def get_column_count(self):
        """
        Return the number of columns
        """
        if not self.column_names:
            return 0
        return len(self.column_names)

    def save(self, *args, **kwargs):
        """
        - Set the md5 attribute on save
        """
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

    def get_worldmap_info(self):
        """
        Retrieve any WorldMap info:
            - a WorldMapJoinLayerInfo object or
            - a WorldMapLatLngInfo
        """
        # Is there a related WorldMapLatLngInfo object?
        #
        worldmap_info = self.worldmaplatlnginfo_set.first()
        if worldmap_info is not None:   # Yes, send it
            return worldmap_info

        # Return an available WorldMapJoinLayerInfo object or None
        #
        return self.worldmapjoinlayerinfo_set.first()


    def get_abstract_for_join(self):
        """
        Populate the 'abstract' field when attempting to
        create a WorldMap layer

        This should be editable by the user
        """
        abstract = ('{0}<p><b>File:</b> {1}</p>'
                    '<p><b>Source:</b> Dataverse repository</p>'
                    '').format(self.dataset_citation,\
                        self.datafile_label)
        return abstract




class WorldMapTabularLayerInfo(TimeStampedModel):
    """
    Store the results of a new layer created by:
        (1) Successfully joining a tabular file to an existing layer
        (2) Mapping a file with latitude/longitude columns

    The file types are distinguished by the "is_join_layer"
    """

    tabular_info = models.ForeignKey(TabularFileInfo)

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
        verbose_name = 'WorldMapTabularLayerInfo'
        verbose_name_plural = verbose_name

    def get_unmapped_record_count(self):
        """
        Differs according to record type
        """
        assert False, "This must be implemented in concrete classes"

    def did_any_rows_map(self):
        """
        Check the mapping result for the number of mapped records
        """
        assert False, "This must be implemented in concrete classes"


    def is_lat_lng_layer(self):
        """
        Is this the result of mapping Lat/Lng columns?
        (Overridden in concrete class)
        """
        return False

    def is_join_layer(self):
        """
        Is this the result of joining an existing layer?
        (Overridden in concrete class)
        """
        return False

    def get_worldmap_info(self):
        """
        Must be defined in concrete classes
        """
        assert False, "This method must be defined in inheriting models"


    @staticmethod
    def format_attribute_maplink_data_from_string(pyobj_string):
        try:
            return eval(pyobj_string)
        except:
            LOGGER.error('Failed to use eval to convert string to python object: %s' % pyobj_string)
            return None


    @staticmethod
    def build_from_worldmap_json(tabular_info, json_dict):
        """
        Create WorldMapTabularLayerInfo object using
        a python dictionary containing information
        returned from the WorldMapLayerInfo.

        (Also used to check if a layer exists)
        """
        #print 'build_from_worldmap_json'
        #print 'tabular_info', tabular_info
        #print 'json_dict', json_dict

        if tabular_info is None:
            LOGGER.error('tabular_info cannot be None')
            return None

        if json_dict is None:
            LOGGER.error('json_dict cannot be None')
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

        attribute_data = WorldMapTabularLayerInfo.format_attribute_maplink_data_from_string(core_data['attribute_info'])
        if attribute_data is None:
            LOGGER.error('Failed to convert core_data "attribute_info" from string to python object (list)')
            return None
        #    attribute_data = ''

        # -----------------------------------------
        # Get download_links (optional)
        # Note: Currently this is an escaped string within core data...
        # -----------------------------------------
        if 'download_links' in core_data:
            download_links =  WorldMapTabularLayerInfo.format_attribute_maplink_data_from_string(core_data['download_links'])

            if download_links is None:
                LOGGER.error('Failed to convert core_data "download_links" from string to python object (list)')
                download_links = ''
        else:
            download_links = ''

        # -----------------------------------------
        # Gather initial values
        # -----------------------------------------
        init_data = dict(tabular_info=tabular_info,\
                    core_data=core_data,\
                    attribute_data=attribute_data,\
                    download_links=download_links)

        # -----------------------------------------
        # Is this a tabular join or lat/lng map?
        # -----------------------------------------
        attrs_indicating_a_join = ('tablejoin_id',\
                'join_layer_id',\
                'join_layer_typename')
        if all(k in core_data for k in attrs_indicating_a_join):
            # Looks like a TableJoin
            SelectedWorldMapLayerInfoType = WorldMapJoinLayerInfo
        else:
            # Assume it's a LatLng
            SelectedWorldMapLayerInfoType = WorldMapLatLngInfo

        # Create the object
        wm_info = SelectedWorldMapLayerInfoType(**init_data)

        # Save it
        wm_info.save()

        # Clear dupe layers, if any
        WorldMapTabularLayerInfo.clear_duplicate_worldmap_info_objects(wm_info)

        return wm_info

    @staticmethod
    def clear_duplicate_worldmap_info_objects(worldmap_info):
        """
        wm_info_object - instance of a WorldMapLatLngInfo or WorldMapJoinLayerInfo
        """
        if worldmap_info is None or not worldmap_info.id:
            # Make sure the object has been saved -- e.g. has an 'id'
            return
        assert hasattr(worldmap_info, 'is_lat_lng_layer'),\
            ("wm_info_object must be a WorldMapJoinLayerInfo"
             " or WorldMapLatLngInfo object")

        if worldmap_info.is_lat_lng_layer():
            SelectedWorldMapLayerInfoType = WorldMapLatLngInfo
        else:
            SelectedWorldMapLayerInfoType = WorldMapJoinLayerInfo

        # Delete similar objects - same tabular file + same WorldMap layer
        # Bit of a hack due to fuzzy requirements early on
        # whether a tab file can have more than one map -- currently allowing
        #
        filters = dict(tabular_info=worldmap_info.tabular_info,\
                        layer_name=worldmap_info.layer_name)

        # Pull objects except the current "worldmap_info"
        #
        older_info_objects = SelectedWorldMapLayerInfoType.objects.filter(\
                        **filters).exclude(id=worldmap_info.id)

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

    def get_legend_img_url(self):
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
        print ('params:', params)
        param_str = '&'.join(['%s=%s' % (k, v) for k, v in params])
        print ('\n\nparam_str:', param_str)

        return '%s/geoserver/wms?%s' % (self.get_layer_url_base(), param_str)

        """
        Example of how an image tag is formed:
        <img src="{{ worldmap_layerinfo.get_layer_url_base }}/geoserver/wms?request=GetLegendGraphic&format=image/png&width=20&height=20&layer={{ worldmap_layerinfo.layer_name }}&legend_options=fontAntiAliasing:true;fontSize:12;&trefresh={% now "U" %}" id="legend_img" alt="legend" />
        """

    def get_dict_for_classify_form(self):
        """
        Parameters used for populating the classification form
        # Override in concrete class
        """
        pass


    def get_dataverse_server_url(self):
        """
        Retrieve the Dataverse base url to be used
        for using the Dataverse API
        """
        if not self.tabular_info:
            return None

        return self.tabular_info.get_dataverse_server_url()


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


    def get_params_to_check_for_existing_layer_metadata(self):

        assert self.tabular_info is not None, "self.tabular_info cannot be None"

        f = CheckForExistingLayerForm(self.tabular_info.__dict__)
        if not f.is_valid():
            raise forms.ValidationError(\
                'CheckForExistingLayerForm params did not validate: %s'\
                 % f.errors)

        return f.cleaned_data


    def get_params_for_dv_delete_layer_metadata(self):

        f = GeoconnectToDataverseDeleteMapLayerMetadataForm(\
                {'dv_session_token' : self.tabular_info.dv_session_token})
        if not f.is_valid():
            raise forms.ValidationError(\
                'WorldMapLayerInfo DELETE params did not validate: %s' %\
                 f.errors)

        return f.format_for_dataverse_api()

    #@staticmethod
    #def get_existing_info(**params_for_existing_check):


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
                full_link = self.core_data.get('map_image_link',  None)
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


    def get_params_for_dv_update(self):
        """
        Format data to send to the Dataverse
        """
        # Hack for the layer_link
        self.verify_layer_link_format()
        if self.core_data and self.core_data.get('joinDescription') is None:
            self.core_data['joinDescription'] = 'Layer created from tabular file'
            self.save()

        f = GeoconnectToDataverseMapLayerMetadataValidationForm(self.core_data)
        if not f.is_valid():
            raise forms.ValidationError('WorldMapLayerInfo params did not validate: %s' % f.errors)

        return f.format_data_for_dataverse_api(self.tabular_info.dv_session_token)


class  WorldMapJoinLayerInfo(WorldMapTabularLayerInfo):
    """
    New Layer created by Joining a DataTable to an Existing Layer
    """
    join_description = models.TextField(blank=True)
    #join_attribute_created = models.CharField(blank=True,\
    #                    max_length=255,\
    #                    help_text="Join attribute created")

    def save(self, *args, **kwargs):

        if not self.id:
            super(WorldMapJoinLayerInfo, self).save(*args, **kwargs)

        self.layer_name = self.core_data.get('layer_typename', None)
        if self.layer_name is None:
            self.layer_name = self.core_data.get('layer_name')


        self.md5 = md5('%s-%s' % (self.id, self.layer_name)).hexdigest()
        super(WorldMapJoinLayerInfo, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'WorldMap Tabular Join Layer Information'
        verbose_name_plural = verbose_name

    def is_lat_lng_layer(self):
        return False

    def is_join_layer(self):
        return True

    def did_any_rows_map(self):
        """
        Check the mapping result for the number of mapped records
        """
        if not self.core_data:
            return False

        #if not 'matched_records_count' in  self.core_data:
        #    return False

        if self.core_data.get('matched_records_count', 0) > 0:
            return True

        return False

    def get_unmapped_record_count(self):
        """
        Return the unmapped record count.

        If no data is available, return -1
        """
        if not self.core_data:
            return -1

        return self.core_data.get('unmatched_record_count', -1)


    def get_params_for_dv_update(self):
        """
        Format data to send to the Dataverse
        """
        self.verify_layer_link_format()
        if self.core_data and self.core_data.get('joinDescription') is None:
            self.core_data['joinDescription'] = 'Layer created from joining to an existing layer'
            self.save()

        f = GeoconnectToDataverseMapLayerMetadataValidationForm(self.core_data)
        if not f.is_valid():
            raise forms.ValidationError('WorldMapLayerInfo params did not validate: %s' % f.errors)

        return f.format_data_for_dataverse_api(self.tabular_info.dv_session_token,\
                        join_description=self.core_data['joinDescription'])

    def get_dict_for_classify_form(self):
        """
        Parameters used for populating the classification form
        # Override in concrete class
        """
        return dict(layer_name=self.layer_name,
                data_source_type=TYPE_JOIN_LAYER,
                raw_attribute_info=self.attribute_data)

"""
from apps.gis_tabular.models import *
w = WorldMapJoinLayerInfo.objects.first()
"""


class WorldMapLatLngInfo(WorldMapTabularLayerInfo):
    """
    New Layer created by Joining a DataTable to an Existing Layer
    """
    def save(self, *args, **kwargs):
        """
        - Set the layer_name based on the JSON core_data
        - Create an md5 value
        """
        if not self.id:
            super(WorldMapLatLngInfo, self).save(*args, **kwargs)

        self.layer_name = self.core_data.get('layer_typename', None)
        if self.layer_name is None:
            self.layer_name = self.core_data.get('layer_name')

        self.md5 = md5('%s-%s' % (self.id, self.layer_name)).hexdigest()
        super(WorldMapLatLngInfo, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'WorldMap Latitude/Longitude Layer Information'
        verbose_name_plural = verbose_name


    def get_params_for_dv_update(self):
        """
        Format data to send to the Dataverse
        """
        self.verify_layer_link_format()
        if self.core_data and self.core_data.get('joinDescription') is None:
            self.core_data['joinDescription'] = 'Layer created from mapping the Latitude and Longitude columnns'
            self.save()

        f = GeoconnectToDataverseMapLayerMetadataValidationForm(self.core_data)
        if not f.is_valid():
            raise forms.ValidationError('WorldMapLayerInfo params did not validate: %s' % f.errors)

        return f.format_data_for_dataverse_api(self.tabular_info.dv_session_token,\
                        join_description=self.core_data['joinDescription'])


    def did_any_rows_map(self):
        """
        The APIs for joint
        """
        if not self.core_data:
            return False

        if self.core_data.get('mapped_record_count', 0) > 0:
            return True

        return False

    def get_unmapped_record_count(self):
        """
        Return the unmapped record count.

        If no data is available, return -1
        """
        if not self.core_data:
            return -1

        return self.core_data.get('unmapped_record_count', -1)


    def is_lat_lng_layer(self):
        return True

    def is_join_layer(self):
        return False

    def get_dict_for_classify_form(self):
        """
        Parameters used for populating the classification form
        # Override in concrete class
        """
        return dict(layer_name=self.layer_name,
                data_source_type=TYPE_LAT_LNG_LAYER,
                raw_attribute_info=self.attribute_data)


class TestIt(TimeStampedModel):
    name = models.CharField(max_length=255, blank=True)        #   file basename

    column_names = jsonfield.JSONField(blank=True, help_text='Saved as a json list')


"""
Example WorldMap response from successfully creating a join layer:

    {u'message': u'worked', u'data': {u'tablejoin_id': 206, u'matched_record_count': 156, u'attribute_info': u'[{"type": "unicode", "display_name": "fid", "name": "fid"}, {"type": "unicode", "display_name": "the_geom_col", "name": "the_geom_col"}, {"type": "int", "display_name": "objectid", "name": "objectid"}, {"type": "float", "display_name": "area", "name": "area"}, {"type": "float", "display_name": "perimeter", "name": "perimeter"}, {"type": "int", "display_name": "state", "name": "state"}, {"type": "unicode", "display_name": "county", "name": "county"}, {"type": "unicode", "display_name": "tract", "name": "tract"}, {"type": "int", "display_name": "ct_id", "name": "ct_id"}, {"type": "unicode", "display_name": "logrecno", "name": "logrecno"}, {"type": "int", "display_name": "blk_count", "name": "blk_count"}, {"type": "float", "display_name": "dry_pct", "name": "dry_pct"}, {"type": "float", "display_name": "dry_acres", "name": "dry_acres"}, {"type": "float", "display_name": "dry_sqmi", "name": "dry_sqmi"}, {"type": "float", "display_name": "dry_sqkm", "name": "dry_sqkm"}, {"type": "float", "display_name": "shape_area", "name": "shape_area"}, {"type": "float", "display_name": "shape_len", "name": "shape_len"}, {"type": "int", "display_name": "hoods_pd_i", "name": "hoods_pd_i"}, {"type": "unicode", "display_name": "nbhd", "name": "nbhd"}, {"type": "unicode", "display_name": "nbhdcrm", "name": "nbhdcrm"}, {"type": "unicode", "display_name": "nsa_id_1", "name": "nsa_id_1"}, {"type": "unicode", "display_name": "nsa_name", "name": "nsa_name"}, {"type": "int", "display_name": "uniqueid", "name": "uniqueid"}, {"type": "int", "display_name": "uniqueid_1", "name": "uniqueid_1"}, {"type": "int", "display_name": "ct_id_1", "name": "ct_id_1"}, {"type": "unicode", "display_name": "nbhd_1", "name": "nbhd_1"}, {"type": "int", "display_name": "b19013_med", "name": "b19013_med"}, {"type": "float", "display_name": "walkabilit", "name": "walkabilit"}, {"type": "float", "display_name": "quality_of", "name": "quality_of"}]', u'layer_join_attribute': u'TRACT', u'worldmap_username': u'rp', u'join_layer_id': u'643', u'download_links': u'{"zip": "http://localhost:8000/download/wfs/643/zip?outputFormat=SHAPE-ZIP&service=WFS&request=GetFeature&format_options=charset%3AUTF-8&typename=geonode%3Ajoin_boston_census_blocks_0zm_boston_income_01tab_2_1&version=1.0.0", "gml": "http://localhost:8000/download/wfs/643/gml?outputFormat=text%2Fxml%3B+subtype%3Dgml%2F3.1.1&service=WFS&request=GetFeature&format_options=charset%3AUTF-8&typename=geonode%3Ajoin_boston_census_blocks_0zm_boston_income_01tab_2_1&version=1.0.0", "tiff": "http://localhost:8000/download/wms/643/tiff?layers=geonode%3Ajoin_boston_census_blocks_0zm_boston_income_01tab_2_1&width=658&bbox=-71.190862998%2C42.2278900021%2C-70.9862559994%2C42.3987970009&service=WMS&format=image%2Fgeotiff&srs=EPSG%3A4326&request=GetMap&height=550", "KML": "http://localhost:8000/download/wms_kml/643/kml?layers=geonode%3Ajoin_boston_census_blocks_0zm_boston_income_01tab_2_1&mode=refresh", "jpg": "http://localhost:8000/download/wms/643/jpg?layers=geonode%3Ajoin_boston_census_blocks_0zm_boston_income_01tab_2_1&width=658&bbox=-71.190862998%2C42.2278900021%2C-70.9862559994%2C42.3987970009&service=WMS&format=image%2Fjpeg&srs=EPSG%3A4326&request=GetMap&height=550", "json": "http://localhost:8000/download/wfs/643/json?outputFormat=json&service=WFS&request=GetFeature&format_options=charset%3AUTF-8&typename=geonode%3Ajoin_boston_census_blocks_0zm_boston_income_01tab_2_1&version=1.0.0", "pdf": "http://localhost:8000/download/wms/643/pdf?layers=geonode%3Ajoin_boston_census_blocks_0zm_boston_income_01tab_2_1&width=658&bbox=-71.190862998%2C42.2278900021%2C-70.9862559994%2C42.3987970009&service=WMS&format=application%2Fpdf&srs=EPSG%3A4326&request=GetMap&height=550", "csv": "http://localhost:8000/download/wfs/643/csv?outputFormat=csv&service=WFS&request=GetFeature&format_options=charset%3AUTF-8&typename=geonode%3Ajoin_boston_census_blocks_0zm_boston_income_01tab_2_1&version=1.0.0", "xls": "http://localhost:8000/download/wfs/643/xls?outputFormat=excel&service=WFS&request=GetFeature&format_options=charset%3AUTF-8&typename=geonode%3Ajoin_boston_census_blocks_0zm_boston_income_01tab_2_1&version=1.0.0", "png": "http://localhost:8000/download/wms/643/png?layers=geonode%3Ajoin_boston_census_blocks_0zm_boston_income_01tab_2_1&width=658&bbox=-71.190862998%2C42.2278900021%2C-70.9862559994%2C42.3987970009&service=WMS&format=image%2Fpng&srs=EPSG%3A4326&request=GetMap&height=550"}', u'unmatched_records_list': u'', u'layer_typename': u'geonode:join_boston_census_blocks_0zm_boston_income_01tab_2_1', u'join_layer_url': u'/data/geonode:join_boston_census_blocks_0zm_boston_income_01tab_2_1', u'join_layer_typename': u'geonode:join_boston_census_blocks_0zm_boston_income_01tab_2_1', u'table_name': u'boston_income_01tab_2_1', u'embed_map_link': u'http://localhost:8000/maps/embed/?layer=geonode:join_boston_census_blocks_0zm_boston_income_01tab_2_1', u'unmatched_record_count': 0, u'layer_link': u'http://localhost:8000/data/geonode:join_boston_census_blocks_0zm_boston_income_01tab_2_1', u'table_id': 332, u'map_image_link': u'http://localhost:8000/download/wms/643/png?layers=geonode%3Ajoin_boston_census_blocks_0zm_boston_income_01tab_2_1&width=658&bbox=-71.190862998%2C42.2278900021%2C-70.9862559994%2C42.3987970009&service=WMS&format=image%2Fpng&srs=EPSG%3A4326&request=GetMap&height=550', u'llbbox': u'[-71.1908629979881, 42.2278900020655, -70.9862559993925, 42.3987970008647]', u'table_join_attribute': u'tract', u'layer_name': u'geonode:join_boston_census_blocks_0zm_boston_income_01tab_2_1', u'tablejoin_view_name': u'join_boston_census_blocks_0zm_boston_income_01tab_2_1'}, u'success': True}
"""

"""
Test with dataverse update:
{'mapLayerLinks': u"{u'zip': u'http://localhost:8000/download/wfs/643/zip?outputFormat=SHAPE-ZIP&service=WFS&request=GetFeature&format_options=charset%3AUTF-8&typename=geonode%3Ajoin_boston_census_blocks_0zm_boston_income_01tab_2_1&version=1.0.0', u'gml': u'http://localhost:8000/download/wfs/643/gml?outputFormat=text%2Fxml%3B+subtype%3Dgml%2F3.1.1&service=WFS&request=GetFeature&format_options=charset%3AUTF-8&typename=geonode%3Ajoin_boston_census_blocks_0zm_boston_income_01tab_2_1&version=1.0.0', u'tiff': u'http://localhost:8000/download/wms/643/tiff?layers=geonode%3Ajoin_boston_census_blocks_0zm_boston_income_01tab_2_1&width=658&bbox=-71.190862998%2C42.2278900021%2C-70.9862559994%2C42.3987970009&service=WMS&format=image%2Fgeotiff&srs=EPSG%3A4326&request=GetMap&height=550', u'KML': u'http://localhost:8000/download/wms_kml/643/kml?layers=geonode%3Ajoin_boston_census_blocks_0zm_boston_income_01tab_2_1&mode=refresh', u'jpg': u'http://localhost:8000/download/wms/643/jpg?layers=geonode%3Ajoin_boston_census_blocks_0zm_boston_income_01tab_2_1&width=658&bbox=-71.190862998%2C42.2278900021%2C-70.9862559994%2C42.3987970009&service=WMS&format=image%2Fjpeg&srs=EPSG%3A4326&request=GetMap&height=550', u'json': u'http://localhost:8000/download/wfs/643/json?outputFormat=json&service=WFS&request=GetFeature&format_options=charset%3AUTF-8&typename=geonode%3Ajoin_boston_census_blocks_0zm_boston_income_01tab_2_1&version=1.0.0', u'pdf': u'http://localhost:8000/download/wms/643/pdf?layers=geonode%3Ajoin_boston_census_blocks_0zm_boston_income_01tab_2_1&width=658&bbox=-71.190862998%2C42.2278900021%2C-70.9862559994%2C42.3987970009&service=WMS&format=application%2Fpdf&srs=EPSG%3A4326&request=GetMap&height=550', u'csv': u'http://localhost:8000/download/wfs/643/csv?outputFormat=csv&service=WFS&request=GetFeature&format_options=charset%3AUTF-8&typename=geonode%3Ajoin_boston_census_blocks_0zm_boston_income_01tab_2_1&version=1.0.0', u'xls': u'http://localhost:8000/download/wfs/643/xls?outputFormat=excel&service=WFS&request=GetFeature&format_options=charset%3AUTF-8&typename=geonode%3Ajoin_boston_census_blocks_0zm_boston_income_01tab_2_1&version=1.0.0', u'png': u'http://localhost:8000/download/wms/643/png?layers=geonode%3Ajoin_boston_census_blocks_0zm_boston_income_01tab_2_1&width=658&bbox=-71.190862998%2C42.2278900021%2C-70.9862559994%2C42.3987970009&service=WMS&format=image%2Fpng&srs=EPSG%3A4326&request=GetMap&height=550'}", 'GEOCONNECT_TOKEN': u'71abfcf55d3895b98348681ffdb34f40430f398443ccc268f94b0171504bd608', 'joinDescription': u'Table joined to layer XYZ by census tract', 'embedMapLink': u'http://localhost:8000/maps/embed/?layer=geonode:join_boston_census_blocks_0zm_boston_income_01tab_2_1', 'mapImageLink': u'http://localhost:8000/download/wms/643/png?layers=geonode:join_boston_census_blocks_0zm_boston_income_01tab_2_1&width=658&bbox=-71.1909,42.2279,-70.9863,42.3988&service=WMS&format=image/png&srs=EPSG:4326&request=GetMap&height=550', 'worldmapUsername': u'rp', 'layerName': u'geonode:join_boston_census_blocks_0zm_boston_income_01tab_2_1', 'layerLink': u'http://localhost:8000/data/geonode:join_boston_census_blocks_0zm_boston_income_01tab_2_1', 'LatLngBoundingBox': u'[-71.1908629979881, 42.2278900020655, -70.9862559993925, 42.3987970008647]'}
"""
