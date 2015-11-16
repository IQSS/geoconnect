from __future__ import absolute_import

from collections import OrderedDict
from hashlib import md5
import json

from urlparse import urlparse

from django.db import models
from django import forms
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from django.conf import settings

from jsonfield import JSONField

from apps.core.models import TimeStampedModel

from apps.gis_basic_file.models import GISDataFile
from shared_dataverse_information.map_layer_metadata.models import MapLayerMetadata
from shared_dataverse_information.map_layer_metadata.forms import MapLayerMetadataValidationForm\
                                                , GeoconnectToDataverseMapLayerMetadataValidationForm\
                                                , GeoconnectToDataverseDeleteMapLayerMetadataForm
from shared_dataverse_information.dataverse_info.forms_existing_layer import CheckForExistingLayerForm

from geo_utils.json_field_reader import JSONFieldReader
from geo_utils.message_helper_json import MessageHelperJSON
from geo_utils.msg_util import *


# Attributes that are copied from GISDataFile to WorldMapImportAttempt
# WorldMapImportAttempt is kept as a log.  GISDataFile is less persistent, deleted within days or weeks
#
DV_SHARED_ATTRIBUTES = ['dv_user_id', 'dv_user_email', 'dv_username', 'datafile_id', 'dataset_version_id']

class WorldMapImportAttempt(TimeStampedModel):
    """
    Record the use of the WorldMap Import API.  This object records details including the DV user and file which will be sent to the WorldMap for import via API.

    The result of the API call will be saved in either a :model:`worldmap_connect.WorldMapLayerInfo` or :model:`worldmap_connect.WorldMapImportFail` object
    """
    title = models.CharField(max_length=255)
    abstract = models.TextField()
    shapefile_name = models.CharField(max_length=255)

    gis_data_file = models.ForeignKey(GISDataFile, on_delete=models.CASCADE)  # ties back to user info

    import_success = models.BooleanField(default=False)

    # Dataverse User Info
    dv_user_id = models.IntegerField(default=-1)          # copied from GISDataFile for audit
    dv_user_email = models.EmailField(blank=True)          # copied from GISDataFile for audit
    dv_username = models.CharField(max_length=255, blank=True)  # copied from GISDataFile for audit

    # Dataverse Datafile Info
    datafile_id = models.IntegerField(default=-1)  # copied from GISDataFile for audit
    dataset_version_id = models.BigIntegerField(default=-1)  # copied from GISDataFile for audit


    def __unicode__(self):
        return '%s %s id:%s, version:%s' % (self.dv_user_email, self.title, self.datafile_id, self.dataset_version_id)


    def get_dataverse_server_url(self):
        assert self.gis_data_file is not None, "For WorldMapImportAttempt's get_dataverse_server_url() self.gis_data_file cannot be None"

        return self.gis_data_file.get_dataverse_server_url()

    def edit_shapefile(self):
        if not self.gis_data_file:
            return 'n/a'
        edit_url = reverse('admin:gis_shapefiles_shapefileinfo_change', args=(self.gis_data_file.id,))
        return '<a href="%s">edit GIS file info</a>' % edit_url
    edit_shapefile.allow_tags = True


    def get_fail_info(self):
        fail_info_list = self.worldmapimportfail_set.all().order_by('-modified')
        return fail_info_list


    def get_success_info(self):
        """
        Modify this to only retrieve the latest WorldMapLayerInfo object

        :returns: latest WorldMapLayerInfo or None
        """
        return self.worldmaplayerinfo_set.order_by('-modified').first()


    def did_import_succeed(self):
        # find successful import attempts
        if self.worldmaplayerinfo_set.count() > 0:
            self.import_success = True
            self.save()
            return True

        self.import_success = False
        self.save()
        return True


    def save(self, *args, **kwargs):
        """
        Fill in Dataverse user and dataset information from the GISDataFile object -- this only happens once
        """
        if self.gis_data_file and self.dv_user_id < 0:
            for attr in DV_SHARED_ATTRIBUTES:
                print attr, getattr(self.gis_data_file, attr)
                setattr(self, attr, getattr(self.gis_data_file, attr))
        super(WorldMapImportAttempt, self).save(*args, **kwargs)


    @staticmethod
    def get_import_attempts(shapefile_info):
        """
        Search for existing WorldMapImportAttempt objects where the params in DV_SHARED_ATTRIBUTES match

        :param shapefile_info: ShapefileInfo object
        :returns: queryset -- either containing WorldMapImportAttempt objects or empty
        """
        if shapefile_info is None:
            return None

        lookup_params = {}
        for attr in DV_SHARED_ATTRIBUTES:
            lookup_params[attr] = getattr(shapefile_info, attr)

        return WorldMapImportAttempt.objects.filter(**lookup_params).order_by('-modified')


    @staticmethod
    def get_latest_attempt(shapefile_info):
        """
        Get the latest WorldMapImportAttempt object where the params in DV_SHARED_ATTRIBUTES match

        :param shapefile_info: ShapefileInfo object
        :returns: latest WorldMapImportAttempt object or None.  "latest" means most recently modified date
        """
        if shapefile_info is None:
            return None

        lookup_params = {}
        for attr in DV_SHARED_ATTRIBUTES:
            lookup_params[attr] = getattr(shapefile_info, attr)

        latest_attempt = WorldMapImportAttempt.objects.filter(**lookup_params).order_by('-modified').first()
        if not latest_attempt:
            return None

        # If latest_attempt doesn't have a reference to the shapefile_info,
        # then make one
        if not latest_attempt.gis_data_file:
            latest_attempt.gis_data_file = shapefile_info
            latest_attempt.save()

        # return the latest_attempt
        return latest_attempt


    class Meta:
        ordering = ('-modified',)


class WorldMapImportFail(TimeStampedModel):
    import_attempt = models.ForeignKey(WorldMapImportAttempt)
    msg = models.TextField()
    orig_response = models.TextField('original response', blank=True)


    def __unicode__(self):
        return '%s' % self.import_attempt

    class Meta:
        ordering = ('-modified',)


class WorldMapLayerInfo(MapLayerMetadata):
    """
    Record the results of a success WorldMap visualization.

    Inherit from shared_dataverse_information.map_layer_metadata.models.MapLayerMetadata
    """
    import_attempt = models.ForeignKey(WorldMapImportAttempt)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    # for object identification
    md5 = models.CharField(max_length=40, blank=True, db_index=True, help_text='auto-filled on save')


    class Meta:
        ordering = ('-modified',)
        verbose_name = 'WorldMapLayerInfo'
        verbose_name_plural = verbose_name


    def save(self, *args, **kwargs):
        if not self.id:
            super(WorldMapLayerInfo, self).save(*args, **kwargs)

        self.md5 = md5('%s-%s' % (self.id, self.layer_name)).hexdigest()
        super(WorldMapLayerInfo, self).save(*args, **kwargs)


    def get_dataverse_server_url(self):
        assert self.import_attempt is not None, "self.import_attempt cannot be None, when calling WorldMapLayerInfo 'get_dataverse_server_url'"

        return self.import_attempt.get_dataverse_server_url()


    def get_layer_url_base(self):
        if not self.layer_link:
            return None

        parsed_url = urlparse(self.layer_link)

        return '%s://%s' % (parsed_url.scheme, parsed_url.netloc)

    def get_legend_img_url(self):
        """
        Construct a url that returns a Legend for a Worldmap layer in the form of PNG file
        """
        if not self.layer_link:
            return None

        params = (('request', 'GetLegendGraphic')\
                   , ('format', 'image/png')\
                   , ('width', 20)\
                   , ('height', 20)\
                   , ('layer', self.layer_name)\
                   , ('legend_options', 'fontAntiAliasing:true;fontSize:11;')\
                )
        print ('params:', params)
        param_str = '&'.join(['%s=%s' % (k, v) for k, v in params ])
        print ('\n\nparam_str:', param_str)

        return '%s/geoserver/wms?%s' % (self.get_layer_url_base(), param_str)

        #<img src="{{ worldmap_layerinfo.get_layer_url_base }}/geoserver/wms?request=GetLegendGraphic&format=image/png&width=20&height=20&layer={{ worldmap_layerinfo.layer_name }}&legend_options=fontAntiAliasing:true;fontSize:12;&trefresh={% now "U" %}" id="legend_img" alt="legend" />

    def add_attribute_info_as_json_string(self, json_string):
        assert json_string is not None, "json_string cannot be None"

        if not JSONFieldReader.is_string_convertible_json(json_string):
            raise TypeError('Could not convert JSON to python: %s' % json_string)

        self.attribute_info = json_string


    def add_attribute_info(self, l=[]):
        assert isinstance(l, list), "l must be a list.  Found class/type (%s/%s)" % (l.__class__.__name__, type(l))

        self.attribute_info = JSONFieldReader.get_python_val_as_json_string(l)

    def get_attribute_info(self):
        return JSONFieldReader.get_json_string_as_python_val(self.attribute_info)

    def get_dict_for_classify_form(self):

        return dict(layer_name=self.layer_name\
                , raw_attribute_info=self.get_attribute_info())

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




    def get_data_dict(self, json_format=False):
        """
        Used for processing model data.
        """
        f = MapLayerMetadataValidationForm(self.__dict__)
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

        f = CheckForExistingLayerForm(self.import_attempt.gis_data_file.__dict__)
        if not f.is_valid():
            raise forms.ValidationError('CheckForExistingLayerForm params did not validate: %s' % f.errors)

        return f.cleaned_data


    def get_params_for_dv_delete_layer_metadata(self):

        f = GeoconnectToDataverseDeleteMapLayerMetadataForm({ 'dv_session_token' : self.import_attempt.gis_data_file.dv_session_token})
        if not f.is_valid():
            raise forms.ValidationError('WorldMapLayerInfo DELETE params did not validate: %s' % f.errors)

        return f.format_for_dataverse_api()


    def get_params_for_dv_update(self):
        """
        Format data to send to the Dataverse
        """
        f = GeoconnectToDataverseMapLayerMetadataValidationForm(self.__dict__)
        if not f.is_valid():
            raise forms.ValidationError('WorldMapLayerInfo params did not validate: %s' % f.errors)

        return f.format_data_for_dataverse_api(self.import_attempt.gis_data_file.dv_session_token)


class JoinTargetInformation(TimeStampedModel):
    """
    Store information retrieved from the WorldMap's JoinTarget API end point.
    This model is used as a "cache" to avoid over calling the API
    """
    name = models.CharField(max_length=255)
    target_info = JSONField()

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.__str__()

    @staticmethod
    def get_formatted_name(geocode_type, year):

        return "{0} ({1})".format(geocode_type, year)


    def get_geocode_types(self):
        assert hasattr(self.target_info, 'has_key'), 'target_info must be a dict'
        assert 'data' in self.target_info, 'target_info must be a "data" key'

        gtypes = []
        for info in self.target_info['data']:
            if not 'geocode_type' in info:
                continue
            if not info['geocode_type'] in gtypes:
                info_line = JoinTargetInformation.get_formatted_name(\
                            info['geocode_type'],\
                            info['year'])
                gtypes.append(info_line)
        return gtypes

    class Meta:
        ordering = ('-created',)


"""
from apps.gis_basic_file.models import *
for g in GISDataFile.objects.all():
    dir(g)

from apps.worldmap_connect.models import *
for wis in WorldMapLayerInfo.objects.all():
    wis.dv_params()
"""
