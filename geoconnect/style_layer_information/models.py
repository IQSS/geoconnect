from hashlib import md5

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.db import models

from core.models import TimeStampedModel

from gis_basic_file.models import GISDataFile


class BinningAlgorithm(TimeStampedModel):
    """Corresponds to the classification tool on the WorldMap
     Examples: Unique values, Quantile, Equal Intervals, Jenks"""
    
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    
    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ('name',)    
        
        
class StyleLayerDescriptionInformation(TimeStampedModel):
    """For a given GIS file, store the styling information, including:
    - Chosen column
    - Binning Algorithm
    - Number of Bins
    - Color Range
    These choices match up with the WorldMap classification tool.
    Roughly corresponds to the WorldMap Style Layer Description (SLD)
    """
    gis_data_file = models.ForeignKey(GISDataFile)
    
    chosen_column = models.CharField(max_length=255)
    binning_algorithm = models.ForeignKey(BinningAlgorithm)
    number_of_bins = models.IntegerField(default=0)

    color_range_start = models.CharField(max_length=30, blank=True)
    color_range_stop = models.CharField(max_length=30, blank=True)
    
    md5 = models.CharField(max_length=40, blank=True, db_index=True)
    

    def __unicode__(self):
        return '%s, %s (%s)' % (self.gis_data_file.name\
                            , self.chosen_column\
                            , self.binning_algorithm\
                            )

    def save(self, *args, **kwargs):
        if not self.id:
            super(StyleLayerDescriptionInformation, self).save(*args, **kwargs)

        self.md5 = md5('%s%s' % (self.id, self.name)).hexdigest()
        super(StyleLayerDescriptionInformation, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Style layer description information'
        verbose_name_plural = verbose_name
        
    