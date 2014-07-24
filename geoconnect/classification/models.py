from django.db import models
from core.models import TimeStampedModel

"""
These values correspond to the same app.models in WorldMap (geonode.classification.models)

The WorldMap values are considered the authoritative source of information.

The values in these models are periodically refreshed.
"""


class ClassificationMethod(TimeStampedModel):
    """Used for the GeoConnect style classification tools 
    """
    display_name = models.CharField(max_length=255)
    value_name = models.CharField(max_length=100, unique=True, help_text='Parameter value in the the geoserver api calls')
    is_string_usable = models.BooleanField(default=False)

    sort_order = models.IntegerField(default=10, help_text='display order for user')
    active = models.BooleanField(default=True)


    def __unicode__(self):
        return  '%s (%s)' % (self.display_name, self.value_name)

    class Meta:
        ordering = ('sort_order', 'display_name')
        

class ColorRamp(TimeStampedModel):
    """Used for the GeoConnect style classification tools 
    
    Note: value names maybe the same--e.g., Custom can have different display names with specific start/end colors
    """
    display_name = models.CharField(max_length=255, unique=True)
    value_name = models.CharField(max_length=100, help_text='Parameter value in the the geoserver api calls')
    sort_order = models.IntegerField(default=10, help_text='display order for user')
    start_color = models.CharField(max_length=30, blank=True, help_text='hex color with "#", as in "#ffcc00"')
    end_color = models.CharField(max_length=30, blank=True, help_text='hex color with "#", as in "#ffcc00"')
    active = models.BooleanField(default=True)
    
    def __unicode__(self):
        return  '%s (%s)' % (self.display_name, self.value_name)

    class Meta:
        ordering = ('sort_order', 'display_name')
