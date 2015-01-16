import logging

from django.shortcuts import render_to_response

from django.http import HttpResponseRedirect, HttpResponse, Http404

from apps.worldmap_connect.form_delete import DeleteMapForm
from apps.dv_notify.metadata_updater import MetadataUpdater

import logging
logger = logging.getLogger('geoconnect')

def view_delete_map(request):
    
    #return HttpResponse('delete')
    if not request.POST:
        raise Http404('Delete Not Found.')
    
    # Check the delete request
    #
    f = DeleteMapForm(request.POST)
    

    if not f.is_valid():

        return HttpResponse('invalid form')

    else:

        worldmap_info = f.get_worldmap_layer_info()

        # -----------------------------------
        # Delete map from WorldMap
        # -----------------------------------
        
        #MetadataUpdater.delete_map_metadata_from_dataverse(worldmap_info)
        
        # -----------------------------------
        # Delete metadata from dataverse
        # -----------------------------------
        (success, err_msg_or_None) = MetadataUpdater.delete_map_metadata_from_dataverse(worldmap_info)
        if not success:
            logger.error("Faild to delete Map Metadata from Dataverse: %s" % err_msg_or_None)
            
        
        return HttpResponse('%s' % worldmap_info)
        return HttpResponse('valid form')

    """
    try:
        shapefile_info = ShapefileInfo.objects.get(md5=shp_md5)
        d['shapefile_info'] = shapefile_info

        except ShapefileInfo.DoesNotExist:
        logger.error('Shapefile not found for hash: %s' % shp_md5)
        raise Http404('Shapefile not found.')
    """