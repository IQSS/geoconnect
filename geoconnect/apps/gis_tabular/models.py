import os
from os.path import basename
from hashlib import md5
from django.utils.text import slugify
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.db import models
from jsonfield import JSONField
from urlparse import urlparse

from apps.core.models import TimeStampedModel

from apps.gis_basic_file.models import GISDataFile, dv_file_system_storage
from geo_utils.json_field_reader import JSONFieldReader
from shared_dataverse_information.map_layer_metadata.models import MapLayerMetadata

SHAPEFILE_MANDATORY_EXTENSIONS = ['.shp', '.shx', '.dbf',]
WORLDMAP_MANDATORY_IMPORT_EXTENSIONS =  SHAPEFILE_MANDATORY_EXTENSIONS + ['.prj']   # '.prj' required for WorldMap shapefile ingest


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

    def __str__(self):
        return self.name

    def test_page(self):
        if not self.id:
            return 'n/a'
        lnk = reverse('view_test_file', kwargs=dict(tabular_id=self.id))
        return '<a href="%s" target="_blank">test page</a>' % lnk
    test_page.allow_tags=True

    def get_dv_file_basename(self):
        if not self.dv_file:
            return None

        return basename(self.dv_file.name)

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



class WorldMapTabularLayerInfo(TimeStampedModel):
    """
    Store the results of a successfully mapped tabular file
    """

    tabular_info = models.ForeignKey(SimpleTabularTest)

    core_data = JSONField()
    attribute_data = JSONField()
    download_links = JSONField(blank=True)

    # for object identification
    md5 = models.CharField(max_length=40, blank=True, db_index=True, help_text='auto-filled on save')



    def save(self, *args, **kwargs):
        if not self.id:
            super(WorldMapTabularLayerInfo, self).save(*args, **kwargs)

        layer_name = self.core_data.get('layer_typename', None)

        self.md5 = md5('%s-%s' % (self.id, layer_name)).hexdigest()
        super(WorldMapTabularLayerInfo, self).save(*args, **kwargs)

    class Meta:
        ordering = ('-modified',)
        verbose_name = 'WorldMapTabularLayerInfo'
        verbose_name_plural = verbose_name

    def get_layer_url_base(self):
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

        layer_name = self.core_data.get('layer_typename', None)
        if layer_name is None:
            return None

        params = (('request', 'GetLegendGraphic')\
                   , ('format', 'image/png')\
                   , ('width', 20)\
                   , ('height', 20)\
                   , ('layer', layer_name)\
                   , ('legend_options', 'fontAntiAliasing:true;fontSize:11;')\
                )
        print ('params:', params)
        param_str = '&'.join(['%s=%s' % (k, v) for k, v in params ])
        print ('\n\nparam_str:', param_str)

        return '%s/geoserver/wms?%s' % (self.get_layer_url_base(), param_str)

        #<img src="{{ worldmap_layerinfo.get_layer_url_base }}/geoserver/wms?request=GetLegendGraphic&format=image/png&width=20&height=20&layer={{ worldmap_layerinfo.layer_name }}&legend_options=fontAntiAliasing:true;fontSize:12;&trefresh={% now "U" %}" id="legend_img" alt="legend" />


    def get_dict_for_classify_form(self):

        layer_name = self.core_data.get('layer_typename', None)

        return dict(layer_name=layer_name\
                , raw_attribute_info=self.column_data)

    '''
    def update_dataverse(self):
        if not self.id:
            return 'n/a'
        lnk = reverse('send_metadata_to_dataverse', kwargs={ 'import_success_id': self.id})
        return lnk
    update_dataverse.allow_tags = True



    def dv_params(self):
        if not self.id:
            return 'n/a'

        lnk = reverse('show_import_success_params', kwargs={ 'import_success_id' : self.id})

        return '<a href="%s">dv params</a>' % lnk
    dv_params.allow_tags = True
    '''



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

        assert self.import_attempt is not None, "self.import_attempt cannot be None"
        assert self.import_attempt.gis_data_file is not None, "self.gis_data_file cannot be None"

        f = CheckForExistingLayerForm(self.tabular_info.__dict__)
        if not f.is_valid():
            raise forms.ValidationError('CheckForExistingLayerForm params did not validate: %s' % f.errors)

        return f.cleaned_data


    def get_params_for_dv_delete_layer_metadata(self):

        f = GeoconnectToDataverseDeleteMapLayerMetadataForm({ 'dv_session_token' : self.tabular_info.dv_session_token})
        if not f.is_valid():
            raise forms.ValidationError('WorldMapLayerInfo DELETE params did not validate: %s' % f.errors)

        return f.format_for_dataverse_api()


    def get_params_for_dv_update(self):
        """
        Format data to send to the Dataverse
        """
        f = GeoconnectToDataverseMapLayerMetadataValidationForm(self.core_data)
        if not f.is_valid():
            raise forms.ValidationError('WorldMapLayerInfo params did not validate: %s' % f.errors)

        return f.format_data_for_dataverse_api(self.tabular_info.dv_session_token)
