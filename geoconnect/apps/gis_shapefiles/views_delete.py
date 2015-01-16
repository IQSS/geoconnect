import logging

from django.shortcuts import render_to_response

from django.http import HttpResponseRedirect, HttpResponse, Http404

from apps.worldmap_connect.form_delete import DeleteMapForm
from apps.dv_notify.metadata_updater import MetadataUpdater

from apps.worldmap_connect.dataverse_layer_services import delete_map_layer


def view_delete_map(request):
    """
    Attempt to delete a dataverse-created WorldMap layer
    """
    
    #return HttpResponse('delete')
    if not request.POST:
        raise Http404('Delete Not Found.')
    
    # Check the delete request
    #
    f = DeleteMapForm(request.POST)
    

    if not f.is_valid():
        return HttpResponse('invalid form')

    else:

        gis_data_file = f.get_gis_data_file_object()
        worldmap_layer_info = f.get_worldmap_layer_info()
        
        # -----------------------------------
        # Delete map from WorldMap
        # -----------------------------------
        delete_map_layer(gis_data_file, worldmap_layer_info)
        ###  TO DO: HERE
        
        # -----------------------------------
        # Delete metadata from dataverse
        # -----------------------------------
        (success, err_msg_or_None) = MetadataUpdater.delete_map_metadata_from_dataverse(worldmap_layer_info)
        if not success:
            logger.error("Faild to delete Map Metadata from Dataverse: %s" % err_msg_or_None)
            
        
        return HttpResponse('%s' % worldmap_layer_info)
        return HttpResponse('valid form')

    """
    try:
        shapefile_info = ShapefileInfo.objects.get(md5=shp_md5)
        d['shapefile_info'] = shapefile_info

        except ShapefileInfo.DoesNotExist:
        logger.error('Shapefile not found for hash: %s' % shp_md5)
        raise Http404('Shapefile not found.')
    """
'''
python manage.py shell

from apps.worldmap_connect.dataverse_layer_services import delete_map_layer
from apps.gis_basic_file.models import GISDataFile
from apps.worldmap_connect.models import WorldMapLayerInfo

gis_data_file = GISDataFile.objects.get(pk=2)
worldmap_layer_info = WorldMapLayerInfo.objects.get(pk=6)

delete_map_layer(gis_data_file, worldmap_layer_info)
'''