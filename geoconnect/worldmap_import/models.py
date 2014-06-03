from django.db import models
from hashlib import md5

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from core.models import TimeStampedModel
from gis_basic_file.models import GISDataFile
from dv_notify.metadata_updater import MetadataUpdater

from geo_utils.json_field_reader import MessageHelperJSON

# Attributes that are copied from GISDataFile to WorldMapImportAttempt
# WorldMapImportAttempt is kept as a log.  GISDataFile is less persistent, deleted within days or weeks
#
DV_SHARED_ATTRIBUTES = ['dv_user_id', 'dv_user_email', 'dv_username', 'datafile_id', 'dataset_version_id']

class WorldMapImportAttempt(TimeStampedModel):
    """
    Record the use of the WorldMap Import API.  This object records details including the DV user and file which will be sent to the WorldMap for import via API. 
    
    The result of the API call will be saved in either a :model:`worldmap_import.WorldMapImportSuccess` or :model:`worldmap_import.WorldMapImportFail` object
    """
    title = models.CharField(max_length=255)
    abstract = models.TextField()
    shapefile_name = models.CharField(max_length=255)

    gis_data_file = models.ForeignKey(GISDataFile, null=True, blank=True, on_delete=models.SET_NULL)  # ties back to user info

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
    
    def get_success_info(self):
        
        success_info_list = self.worldmapimportsuccess_set.all().order_by('-modified')
        if success_info_list.count() > 0:
            return success_info_list[0]
        return None
    
    def did_import_succeed(self):
        # find successful import attempts
        if self.worldmapimportsuccess_set.all().count() > 0:
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
    def get_latest_attempt(shapefile_set):
        """
        Search for existing WorldMapImportAttempt objects where the params in DV_SHARED_ATTRIBUTES match
        """
        if shapefile_set is None:
            return None
        
        lookup_params = {}
        for attr in DV_SHARED_ATTRIBUTES:
            lookup_params[attr] = getattr(shapefile_set, attr)
            
        l = WorldMapImportAttempt.objects.filter(**lookup_params).order_by('-modified')
        
        if l.count() == 0:
            return None
            
        return l[0]
    
    def get_params_for_worldmap_import(self, geoconnect_token=None):
        """
        Prepare partial parameters to send WorldMap import request.
        
        Example of params:
        {'title' : 'Boston Income'\
                , 'abstract' : 'Shapefile containing Boston, MA income levels from 19xx'\
                , 'email' : 'researcher@school.edu'\
                , 'shapefile_name' : 'zipfile_name.zip'\
                , 'geoconnect_token' : 'token-for-api-use'\
                }
        Note: The "geoconnect_token" parameter is provided by the class calling the function.
            At this point it is worldmap_import.WorldMapImporter.
            if a geoconnect_token is not supplied, it will not be included in the params dict
            
        :param geoconnect_token: key used to access the WorldMap API
        :type geoconnect_token: string or None
        :returns: parameters formatted to call the WorldMap import API. 
        :rtype: dict
        """
        d = {}
        d['title'] = self.title
        d['abstract'] = self.abstract
        d['email'] = self.dv_user_email
        d['shapefile_name'] = self.shapefile_name
        if geoconnect_token:
            d['geoconnect_token'] = geoconnect_token
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
        
        
class WorldMapImportSuccess(TimeStampedModel):
    """
    Record the results of a success WorldMap visualization.
    """
    import_attempt = models.ForeignKey(WorldMapImportAttempt)

    worldmap_username = models.CharField(max_length=255)

    layer_name = models.CharField(max_length=255)
    layer_link = models.URLField()
    embed_map_link = models.URLField(blank=True)

    def update_dataverse(self):
        if not self.id:
            return 'n/a'
        print 'blahhhhhhhhhhh'
        lnk = reverse('send_metadata_to_dataverse', kwargs={ 'import_success_id', self.id})
        print '*******************', lnk
        return lnk
        return '<a href="%s">update dataverse</a>' % lnk
    update_dataverse.allow_tags = True 
        
    def get_data_dict(self):
        data_dict = { 'worldmap_username' : self.worldmap_username\
                        , 'layer_name' : self.layer_name\
                        , 'layer_link' : self.layer_link\
                        , 'embed_map_link' : self.embed_map_link\
                    }
        return data_dict
        
    def get_params_for_dv_update(self):
        #['dataset_id', 'layer_name', 'layer_link', 'embed_map_link', 'worldmap_username', 'bbox_min_lng', 'bbox_min_lat', 'bbox_max_lng', 'bbox_max_lat']
        d = self.get_data_dict()

        if self.import_attempt and self.import_attempt.gis_data_file:
            d['dataset_id'] = self.import_attempt.gis_data_file.dataset_id
            
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
    
    class Meta:
        ordering = ('-modified',)

    
    
    
