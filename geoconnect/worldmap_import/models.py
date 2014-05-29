from django.db import models
from hashlib import md5

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from core.models import TimeStampedModel
from gis_basic_file.models import GISDataFile

# Attributes that are copied from GISDataFile to WorldMapImportAttempt
# WorldMapImportAttempt is kept as a log.  GISDataFile is less persistent, deleted within days or weeks
#
DV_SHARED_ATTRIBUTES = ['dv_user_id', 'dv_user_email', 'dv_username', 'dataset_id', 'dataset_version_id']

class WorldMapImportAttempt(TimeStampedModel):
    """
    These objects are *not* deleted from the system
    """
    title = models.CharField(max_length=255)
    abstract = models.TextField()
    shapefile_name = models.CharField(max_length=255)

    gis_data_file = models.ForeignKey(GISDataFile, null=True, blank=True, on_delete=models.SET_NULL)  # ties back to user info

    import_success = models.BooleanField(default=False)
    
    # Dataverse User Info
    dv_user_id = models.IntegerField()          # copied from GISDataFile for audit
    dv_user_email = models.EmailField()          # copied from GISDataFile for audit
    dv_username = models.CharField(max_length=255)  # copied from GISDataFile for audit
    
    # Dataverse Dataset Info
    dataset_id = models.IntegerField()  # copied from GISDataFile for audit
    dataset_version_id = models.IntegerField()  # copied from GISDataFile for audit


    def __unicode__(self):
        return '%s %s id:%s, version:%s' % (self.dv_username, self.title, self.dataset_id, self.dataset_version_id)
    
    def save(self, *args, **kwargs):
        """
        Fill in Dataverse user and dataset information from the GISDataFile object -- this only happens once
        """
        if self.gis_data_file and not self.dv_user_id:
            for attr in DV_SHARED_PARAMS:
                setattr(self, attr, getattr(self.gis_data-file, attr)) 
        super(WorldMapImportAttempt, self).save(*args, **kwargs)
    
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

    def __unicode__(self):
        return '%s' % self.import_attempt
        
    class Meta:
        ordering = ('-modified',)
        
        
class WorldMapImportSuccess(TimeStampedModel):
    import_attempt = models.ForeignKey(WorldMapImportAttempt)

    worldmap_username = models.CharField(max_length=255)

    layer_name = models.CharField(max_length=255)
    layer_link = models.URLField()
    embed_map_link = models.URLField(blank=True)

    def __unicode__(self):
        return '%s' % self.import_attempt
    
    class Meta:
        ordering = ('-modified',)

    
    
    
