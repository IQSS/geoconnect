import os
import json

from django.shortcuts import render_to_response

from django.http import HttpResponseRedirect, HttpResponse
from django.http import Http404
from django.template import RequestContext
from django.core.urlresolvers import reverse

from worldmap_import.models import WorldMapImportSuccess
from worldmap_import.send_shapefile_service import SendShapefileService

from dv_notify.metadata_updater import MetadataUpdater

import logging
logger = logging.getLogger(__name__)

from django.conf import settings


def show_import_success_params(request, import_success_id):

    try:
        wm_success = WorldMapImportSuccess.objects.get(pk=import_success_id)
    except WorldMapImportSuccess.DoesNotExist:
        return HttpResponse('WorldMapImportSuccess object not found: %s' % import_success_id)

    return HttpResponse('%s' % wm_success.get_data_dict())


def send_metadata_to_dataverse(request, import_success_id):
    try:
        wm_success = WorldMapImportSuccess.objects.get(pk=import_success_id)
    except WorldMapImportSuccess.DoesNotExist:
        return HttpResponse('WorldMapImportSuccess object not found: %s' % import_success_id)
    
    MetadataUpdater.update_dataverse_with_metadata(wm_success)
    if wm_success.import_attempt.gis_data_file:
        lnk = reverse('view_shapefile'\
                    , kwargs={ 'shp_md5' : wm_success.import_attempt.gis_data_file.md5 }\
                    )
        return HttpResponseRedirect(lnk)
    return HttpResponse('metadata sent')
    

def view_send_shapefile_to_worldmap(request, shp_md5):
    
    if not shp_md5:
        raise Http404('No shapefile indicated')
    
    shp_service = SendShapefileService(**dict(shp_md5=shp_md5))
    shp_service.send_shapefile_to_worldmap()
    
    if shp_service.has_err:
        # Do something more here!
        print ('-' * 40)
        print ('-- IMPORT TROUBLE --')
        print('\n'.join(shp_service.err_msgs))
        print ('-' * 40)
        
    return HttpResponseRedirect(reverse('view_shapefile', kwargs={'shp_md5': shp_md5 }))
    
    