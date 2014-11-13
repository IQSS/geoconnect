from __future__ import absolute_import

from collections import OrderedDict
from hashlib import md5
import json

from urlparse import urlparse

from django.db import models

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from django.conf import settings

from apps.core.models import TimeStampedModel

from apps.gis_basic_file.dataverse_info_service import get_dataverse_info_dict

from apps.gis_basic_file.models import GISDataFile
#from dataverse_info.forms import DataverseInfoValidationForm

from apps.dv_notify.metadata_updater import MetadataUpdater
from apps.dv_notify.models import KEY_UPDATES_TO_MATCH_DATAVERSE_API

from geo_utils.json_field_reader import JSONFieldReader
from geo_utils.message_helper_json import MessageHelperJSON


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

    gis_data_file = models.ForeignKey(GISDataFile, null=True, blank=True, on_delete=models.CASCADE)  # ties back to user info

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
        
    
    def get_params_for_worldmap_connect(self, geoconnect_token=None):
        """
        Prepare partial parameters to send WorldMap import request.
        
        Example of params:
              {   'title' : 'Boston Income'\
                , 'abstract' : 'Shapefile containing Boston, MA income levels from 19xx'\
                , 'email' : 'researcher@school.edu'\
                , 'shapefile_name' : 'zipfile_name.zip'\
                , settings.WORLDMAP_TOKEN_NAME_FOR_DV : 'token-for-api-use'\
                , 'dataverse_info' : {--DataverseInfo JSON--}
                }
        Note: The "geoconnect_token" parameter is provided by the class calling the function.
            At this point it is worldmap_connect.WorldMapImporter.
            if a geoconnect_token is not supplied, it will not be included in the params dict
            
        :param geoconnect_token: key used to access the WorldMap API
        :type geoconnect_token: string or None
        :returns: parameters formatted to call the WorldMap import API. 
        :rtype: dict
        """
        print ('get_params_for_worldmap_connect')
        d = {}
        d['title'] = self.title
        d['abstract'] = self.abstract
        d['email'] = self.dv_user_email
        d['shapefile_name'] = self.shapefile_name
        print ('get_params_for_worldmap_connect 2', d)
        print '*'*10
        
        #f = DataverseInfoValidationForm(self.gis_data_file.__dict__)
        #if f.is_valid():
        #    dataverse_info = f.cleaned_data
        #print ('get_params_for_worldmap_connect 3', dataverse_info)
        # add dataverse info
        dataverse_info_dict = get_dataverse_info_dict(self.gis_data_file)
        if dataverse_info_dict is not None:
            d.update(dataverse_info_dict)
            #d['dataverse_info'] = get_dataverse_info_dict(self.gis_data_file)
        
        #print 'hooray!'
        if geoconnect_token:
            d[settings.WORLDMAP_TOKEN_NAME_FOR_DV] = geoconnect_token
        return d
    
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
        
        
class WorldMapLayerInfo(TimeStampedModel):
    """
    Record the results of a success WorldMap visualization.
    """
    import_attempt = models.ForeignKey(WorldMapImportAttempt)

    worldmap_username = models.CharField(max_length=255)

    layer_name = models.CharField(max_length=255)
    layer_link = models.URLField()
    embed_map_link = models.URLField(blank=True)

    attribute_info = models.TextField(blank=True, help_text='JSON list of attributes')
    
    # for object identification
    md5 = models.CharField(max_length=40, blank=True, db_index=True, help_text='auto-filled on save')
    
    
    class Meta:
        ordering = ('-modified',)
        verbose_name = 'WorldMap Import Success'
        verbose_name_plural = verbose_name
    
    
    def save(self, *args, **kwargs):
        if not self.id:
            super(WorldMapLayerInfo, self).save(*args, **kwargs)

        self.md5 = md5('%s-%s' % (self.id, self.layer_name)).hexdigest()
        super(WorldMapLayerInfo, self).save(*args, **kwargs)

    
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
        
    
    def add_attribute_info(self, l=[]):
        if not type(l) is list:
            return 

        self.attribute_info = JSONFieldReader.get_python_val_as_json_string(l)

    def get_attribute_info(self):
        return JSONFieldReader.get_json_string_as_python_val(self.attribute_info)
    
    
    def update_dataverse(self):
        if not self.id:
            return 'n/a'
        lnk = reverse('send_metadata_to_dataverse', kwargs={ 'import_success_id', self.id})
        print '*******************', lnk
        return lnk
        return '<a href="%s">update dataverse</a>' % lnk
    update_dataverse.allow_tags = True 
    
    def dv_params(self):
        if not self.id:
            return 'n/a'

        lnk = reverse('show_import_success_params', kwargs={ 'import_success_id' : self.id})

        return '<a href="%s">dv params</a>' % lnk
    dv_params.allow_tags = True 
    
    

    
    def get_data_dict(self):
        data_dict = { 'worldmap_username' : self.worldmap_username\
                        , 'layer_name' : self.layer_name\
                        , 'layer_link' : self.layer_link\
                        , 'embed_map_link' : self.embed_map_link\
                    }
        
        if self.import_attempt.gis_data_file:
            data_dict['datafile_id'] = self.import_attempt.gis_data_file.datafile_id
            data_dict['dv_session_token'] = self.import_attempt.gis_data_file.dv_session_token

            try:
                shapefile_info = self.import_attempt.gis_data_file.shapefileset
                if shapefile_info.bounding_box:
                    bbox = json.loads(shapefile_info.bounding_box)
                    print 'bbox', bbox.__class__.__name__
                    data_dict.update({ 'bbox_min_lng' : bbox[0]
                        , 'bbox_min_lat' : bbox[1]
                        , 'bbox_max_lng' : bbox[2]
                        , 'bbox_max_lat' : bbox[3]
                        })
            except:
                pass
                
        return data_dict
        
        
    def get_params_for_dv_update(self):
        #['datafile_id', 'layer_name', 'layer_link', 'embed_map_link', 'worldmap_username', 'bbox_min_lng', 'bbox_min_lat', 'bbox_max_lng', 'bbox_max_lat', 'dv_session_token']
        d = self.get_data_dict()


        if self.import_attempt and self.import_attempt.gis_data_file:
            d['datafile_id'] = self.import_attempt.gis_data_file.datafile_id
            d['dv_session_token'] = self.import_attempt.gis_data_file.dv_session_token
            try:
                shapefile_info = self.import_attempt.gis_data_file.shapefileset
                if shapefile_info.bounding_box:
                    bbox = json.loads(shapefile_info.bounding_box)
                    print 'bbox', bbox.__class__.__name__
                    d.update({ 'bbox_min_lng' : bbox[0]
                        , 'bbox_min_lat' : bbox[1]
                        , 'bbox_max_lng' : bbox[2]
                        , 'bbox_max_lat' : bbox[3]
                        })
            except:
                pass
                
        
        for old_key, new_key in KEY_UPDATES_TO_MATCH_DATAVERSE_API.items():
            if d.has_key(old_key):
                d[new_key] = d.get(old_key) # add new key name
                d.pop(old_key)  # pop off the old key name
        print (d)
        return d
        


    def get_as_json_message(self):
        """
        Return something like:
        {"message": "", "data": {"layer_link": "http://localhost:8000/data/geonode:income_in_boston_gui_5_zip_q5v", "worldmap_username": "raman_prasad", "layer_name": "geonode:income_in_boston_gui_5_zip_q5v", "embed_map_link": "http://localhost:8000/maps/embed/?layer=geonode:income_in_boston_gui_5_zip_q5v"}, "success": true}    
        """
        data_dict = self.get_data_dict()

        return MessageHelperJSON.get_json_msg(success=True, msg='', data_dict=data_dict)

    def __unicode__(self):
        return '%s' % self.import_attempt
    

"""
from apps.gis_basic_file.models import *
for g in GISDataFile.objects.all():
    dir(g)

from apps.worldmap_connect.models import *
for wis in WorldMapLayerInfo.objects.all():
    wis.dv_params()
"""
    
    
