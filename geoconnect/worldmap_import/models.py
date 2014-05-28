from hashlib import md5
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.db import models
from datetime import date
from gis_basic_file.scratch_directory_services import ScratchDirectoryHelper
import shutil


class WorldMapImportAttempt(models.Model):
    dv_user_email = models.EmailField()
    title = models.CharField(max_length=255)
    abstract = models.TextField()
    shapefile_name = models.CharField(max_length=255)
    
    {'title' : 'Boston Income'\
            , 'abstract' : 'Shapefile containing Boston, MA income levels from 19xx'\
            , 'email' : 'researcher@school.edu'\
            , 'shapefile_name' : 'zipfile_name.zip'\
            , 'geoconnect_token' : 'token-for-api-use'\
            }