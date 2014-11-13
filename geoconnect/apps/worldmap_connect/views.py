import os
import json

from django.shortcuts import render_to_response

from django.http import HttpResponseRedirect, HttpResponse
from django.http import Http404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from apps.worldmap_connect.models import WorldMapLayerInfo
from apps.worldmap_connect.send_shapefile_service import SendShapefileService

from apps.dv_notify.metadata_updater import MetadataUpdater

import logging
logger = logging.getLogger(__name__)

from django.conf import settings

@login_required
def show_import_success_params(request, import_success_id):
    """
    Convenience method for reviewing the parameters
    """
    try:
        wm_success = WorldMapLayerInfo.objects.get(pk=import_success_id)
    except WorldMapLayerInfo.DoesNotExist:
        return HttpResponse('WorldMapLayerInfo object not found: %s' % import_success_id)

    return HttpResponse('%s' % wm_success.get_data_dict())

#@login_required
def send_metadata_to_dataverse(request, import_success_id):
    """
    Send metadata to dataverse: async this!!
    """
    try:
        wm_success = WorldMapLayerInfo.objects.get(pk=import_success_id)
    except WorldMapLayerInfo.DoesNotExist:
        return HttpResponse('WorldMapLayerInfo object not found: %s' % import_success_id)
    
    MetadataUpdater.update_dataverse_with_metadata(wm_success)
    if wm_success.import_attempt.gis_data_file:
        lnk = reverse('view_shapefile'\
                    , kwargs={ 'shp_md5' : wm_success.import_attempt.gis_data_file.md5 }\
                    )
        return HttpResponseRedirect(lnk)
    return HttpResponse('metadata sent')
    
#@login_required
def view_send_shapefile_to_worldmap(request, shp_md5):
    """
    Send shapefile to WorldMap.
    
    Async the SendShapefileService.send_shapefile_to_worldmap process

    For now, it follows the process and then redirects back to the shapefile page with success (and map) or fail messages
    """
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
        
    return HttpResponseRedirect(reverse('view_shapefile_visualize_attempt', kwargs={'shp_md5': shp_md5 }))
    
    