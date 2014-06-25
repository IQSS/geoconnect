import os
from hashlib import md5
import cPickle as pickle

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.db import models

from core.models import TimeStampedModel

from gis_basic_file.models import GISDataFile
from geo_utils.fsize_human_readable import sizeof_fmt
from geo_utils.json_field_reader import JSONFieldReader


class BaseColumnStats(TimeStampedModel):
    
    name = models.CharField(max_length=255)
    num_vals = models.IntegerField()

    num_blanks = models.IntegerField()
    num_errs = models.IntegerField()
    
    class Meta:
        abstract = True
        
        

class StringColumnStats(BaseColumnStats):
    """Store statistics related to string values"""
    frequency_dict = models.TextField(blank=True, help_text='python dict stored as a string')
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    