import os
import json

from django.shortcuts import render_to_response

from django.http import HttpResponseRedirect, HttpResponse
from django.http import Http404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required


from apps.worldmap_connect.models import WorldMapLayerInfo, JoinTargetInformation
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
        worldmap_layer_info = WorldMapLayerInfo.objects.get(pk=import_success_id)
    except WorldMapLayerInfo.DoesNotExist:
        raise Http404('WorldMapLayerInfo object not found: %s' % import_success_id)

    return HttpResponse('%s' % worldmap_layer_info.get_data_dict(json_format=True))


@login_required
def send_metadata_to_dataverse(request, import_success_id):
    """
    Retrieve WorldMapLayerInfo and send it to the Dataverse
    """
    try:
        worldmap_layer_info = WorldMapLayerInfo.objects.get(pk=import_success_id)
    except WorldMapLayerInfo.DoesNotExist:
        return HttpResponse('WorldMapLayerInfo object not found: %s' % import_success_id)


    MetadataUpdater.update_dataverse_with_metadata(worldmap_layer_info)
    if worldmap_layer_info.import_attempt.gis_data_file:
        lnk = reverse('view_shapefile'\
                    , kwargs={ 'shp_md5' : worldmap_layer_info.import_attempt.gis_data_file.md5 }\
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

@login_required
def clear_jointarget_info(request):
    """
    For debugging, clear out any JoinTarget Information
    saved from the WorldMap API
    """
    if not request.user.is_superuser:
        return HttpResponse('must be a superuser')

    l = JoinTargetInformation.objects.all()

    cnt = l.count()
    if cnt == 0:
        return HttpResponse('no JoinTargetInformation objects found')

    l.delete()

    return HttpResponse('%s JoinTargetInformation object(s) deleted' % cnt)
