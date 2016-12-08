import logging

from django.shortcuts import render_to_response
from django.template import RequestContext

from django.conf import settings

from geo_utils.msg_util import *
from geo_utils.view_util import get_common_lookup

from apps.worldmap_connect.form_delete import DeleteMapForm
from apps.dv_notify.metadata_updater import MetadataUpdater
from apps.worldmap_connect.dataverse_layer_services import delete_map_layer


logger = logging.getLogger(__name__)



def view_delete_map(request):
    """
    Attempt to delete a dataverse-created WorldMap layer
    """
    if not request.POST:
        raise Http404('Delete Not Found.')

    lu = get_common_lookup(request)
    lu['WORLDMAP_SERVER_URL'] = settings.WORLDMAP_SERVER_URL
    lu['DATAVERSE_SERVER_URL'] = settings.DATAVERSE_SERVER_URL

    # Check the delete request
    f = DeleteMapForm(request.POST)

    if not f.is_valid():
        lu['ERROR_FOUND'] = True
        lu['FAILED_TO_VALIDATE'] = True
        return render_to_response('gis_shapefiles/view_delete_layer.html',
                                    lu,
                                    context_instance=RequestContext(request))

    # Form params look good
    gis_data_file = f.get_gis_data_file_object()
    worldmap_layer_info = f.get_worldmap_layer_info()

    lu['gis_data_file'] = gis_data_file
    if gis_data_file:
        lu['return_to_dataverse_url'] = gis_data_file.return_to_dataverse_url


    # -----------------------------------
    # Delete map from WorldMap
    # -----------------------------------
    (success, err_msg_or_None) = delete_map_layer(gis_data_file, worldmap_layer_info)
    if success is False:
        logger.error("Failed to delete WORLDMAP layer: %s", err_msg_or_None)

        if err_msg_or_None and err_msg_or_None.find('"Existing layer not found."') > -1:
            pass
        else:
            lu['ERROR_FOUND'] = True
            lu['WORLDMAP_DATA_DELETE_FAILURE'] = True
            lu['ERR_MSG'] = err_msg_or_None
            return render_to_response('gis_shapefiles/view_delete_layer.html',
                                        lu,
                                        context_instance=RequestContext(request))

    # At this point, the layer no longer exists on WorldMap
    #
    worldmap_layer_info.import_attempt.delete()
    #worldmap_layer_info.delete()

    # -----------------------------------
    # Delete metadata from dataverse
    # -----------------------------------

    (success2, err_msg_or_None2) = MetadataUpdater.delete_dataverse_map_metadata(worldmap_layer_info)
    if success2 is False:
        logger.error("Failed to delete Map Metadata from Dataverse: %s", err_msg_or_None)

        lu['ERROR_FOUND'] = True
        lu['DATAVERSE_DATA_DELETE_FAILURE'] = True
        lu['ERR_MSG'] = err_msg_or_None2
        return render_to_response('gis_shapefiles/view_delete_layer.html',
                                    lu,
                                    context_instance=RequestContext(request))



    lu['DELETE_SUCCESS'] = True

    return render_to_response('gis_shapefiles/view_delete_layer.html',
                                    lu,
                                    context_instance=RequestContext(request))


'''
python manage.py shell

from apps.worldmap_connect.dataverse_layer_services import delete_map_layer
from apps.gis_basic_file.models import GISDataFile
from apps.worldmap_connect.models import WorldMapLayerInfo

gis_data_file = GISDataFile.objects.get(pk=2)
worldmap_layer_info = WorldMapLayerInfo.objects.get(pk=6)

delete_map_layer(gis_data_file, worldmap_layer_info)
'''
