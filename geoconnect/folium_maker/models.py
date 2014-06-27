from django.db import models

from core.models import TimeStampedModel
from gis_basic_file.models import GISDataFile
from .folium_directory_services import FoliumDirectoryHelper


class FoliumMap(TimeStampedModel):
    """GeoConnect - For working with a Dataverse File for a given user
    These objects will persist for a limited time (days, weeks), depending on the system demand
    """
    # Dataverse user info
    name = models.CharField(max_length=255)
    
    gis_data_file = models.ForeignKey(GISDataFile)

    folium_output_directory = models.CharField(max_length=255, blank=True, help_text='folium output directory')

    folium_url = models.CharField(max_length=255, blank=True)
    
    def __unicode__(self):
        if self.name:
            return self.name
        return self.id 
        
    
    class Meta:
        ordering = ('-modified',  )
    
    def get_output_directory(self):
        """Return the full path of the scratch working directory.  
        Creates directory if it doesn't exist """
        return FoliumDirectoryHelper.get_output_directory(self)

    def delete_output_directory(self):
        """Deletes the scratch working directory, if it exists"""
        return FoliumDirectoryHelper.delete_output_directory(self)
