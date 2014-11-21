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
from shapefile_import.forms import ShapefileImportDataForm

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
        verbose_name = 'WorldMapLayerInfo'
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
    
    
