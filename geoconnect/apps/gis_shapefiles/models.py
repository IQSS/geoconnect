import os
from hashlib import md5

from django.db import models

import jsonfield # jsonfield.JSONField

from apps.core.models import TimeStampedModel
from apps.gis_basic_file.models import GISDataFile
from geo_utils.fsize_human_readable import sizeof_fmt
from geo_utils.json_field_reader import JSONHelper
from apps.layer_types.static_vals import TYPE_SHAPEFILE_LAYER
from apps.worldmap_layers.models import WorldMapLayerInfo

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


    def get_worldmap_info(self):
        """
        Must be defined in concrete classes
        """
        assert False, "This method must be defined in inheriting models"


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
        WorldMapLayerInfo.clear_duplicate_worldmap_info_objects(wm_info)

        return wm_info



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
        return dict(layer_name=self.layer_name,
                data_source_type=TYPE_SHAPEFILE_LAYER,
                raw_attribute_info=self.attribute_data)


    def get_dataverse_server_url(self):
        """
        Retrieve the Dataverse base url to be used
        for using the Dataverse API
        """
        if not self.shapefile_info:
            return None

        return self.shapefile_info.get_dataverse_server_url()


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

        assert self.shapefile_info is not None, "self.shapefile_info cannot be None"

        f = CheckForExistingLayerForm(self.shapefile_info.__dict__)
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
