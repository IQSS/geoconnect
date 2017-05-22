"""
View to delete Map created from a tabular file.
    - Delete the WorldMap layer
    - Delete the Dataverse metadata
"""
import logging

from django.shortcuts import render
from django.http import HttpResponse, Http404

from django.conf import settings

from gc_apps.geo_utils.msg_util import msg, msgt
from gc_apps.geo_utils.view_util import get_common_lookup
from gc_apps.geo_utils.geoconnect_step_names import PANEL_TITLE_DELETE_MAP,\
    PANEL_TITLE_REMAP

from gc_apps.gis_tabular.forms_delete import DeleteMapForm
from gc_apps.gis_basic_file.models import GISDataFile

from gc_apps.dv_notify.metadata_updater import MetadataUpdater
from gc_apps.worldmap_connect.dataverse_layer_services import delete_map_layer,\
    delete_map_layer_by_cb_dict

from gc_apps.geo_utils.message_helper_json import MessageHelperJSON
from gc_apps.gis_shapefiles.initial_request_helper import InitialRequestHelper

LOGGER = logging.getLogger(__name__)

def view_delete_tabular_map(request):
    """
    Attempt to delete a dataverse-created WorldMap layer
    """
    if not request.POST:
        raise Http404('Delete Not Found.')

    d = get_common_lookup(request)
    d['WORLDMAP_SERVER_URL'] = settings.WORLDMAP_SERVER_URL
    d['DATAVERSE_SERVER_URL'] = settings.DATAVERSE_SERVER_URL

    d['page_title'] = PANEL_TITLE_DELETE_MAP
    d['IS_DELETE_PAGE'] = True
    # Check the delete request
    f = DeleteMapForm(request.POST)

    if not f.is_valid():
        d['ERROR_FOUND'] = True
        d['FAILED_TO_VALIDATE'] = True
        return render(request, 'worldmap_layers/view_delete_layer.html', d)

    # Form params look good
    worldmap_layer_info = f.get_worldmap_layer_info()
    if not worldmap_layer_info:
        raise Http404('WorldMap Layer info no longer available')

    # depending on the type: tabular_info, shapefile_info, etc
    #
    if worldmap_layer_info.is_shapefile_layer():
        d['is_shapefile_layer'] = True
    else:
        d['is_tabular_layer'] = True

    gis_data_info = worldmap_layer_info.get_gis_data_info()

    d['gis_data_info'] = gis_data_info

    # -----------------------------------
    # Delete map from WorldMap
    # -----------------------------------
    flag_delete_local_worldmap_info = False

    (success, err_msg_or_None) = delete_map_layer(gis_data_info, worldmap_layer_info)
    if success is False:
        LOGGER.error("Failed to delete WORLDMAP layer: %s", err_msg_or_None)

        if err_msg_or_None and err_msg_or_None.find('"Existing layer not found."') > -1:
            pass
        else:
            d['ERROR_FOUND'] = True
            d['WORLDMAP_DATA_DELETE_FAILURE'] = True
            d['ERR_MSG'] = err_msg_or_None
            return render(request, 'worldmap_layers/view_delete_layer.html', d)
    else:
        # At this point, the layer no longer exists on WorldMap,
        # set a flag to delete it from geoconnect, even if the Dataverse
        # delete fails
        flag_delete_local_worldmap_info = True

    # -----------------------------------
    # Delete metadata from dataverse
    # -----------------------------------

    (success2, err_msg_or_None2) = MetadataUpdater.delete_dataverse_map_metadata(worldmap_layer_info)

    # Delete the Geoconnect WorldMap info -- regardless of
    # whether the data was removed from Dataverse
    if flag_delete_local_worldmap_info:
        msgt('Delete worldmap_layer_info: %s' % worldmap_layer_info)
        worldmap_layer_info.delete()

    if success2 is False:
        LOGGER.error("Failed to delete Map Metadata from Dataverse: %s", err_msg_or_None)

        d['ERROR_FOUND'] = True
        d['DATAVERSE_DATA_DELETE_FAILURE'] = True
        d['ERR_MSG'] = err_msg_or_None2

        return render(request, 'worldmap_layers/view_delete_layer.html', d)

    d['DELETE_SUCCESS'] = True
    d['page_title'] = PANEL_TITLE_REMAP

    return render(request, 'worldmap_layers/view_delete_layer.html', d)


def view_delete_tabular_map_no_ui(request, dataverse_token):
    """
    Attempt to delete a dataverse-created WorldMap layer via a direct API call, w/out any UI involved.
    Operates on the same token-callback url principle as other geoconnect methods.
    (1) Check incoming url for a callback key 'cb'
        and use the callback url to retrieve the DataverseInfo via a POST
        (this is copied directly from the workflow of the "map-it" method)
        OK, the whole process has been royally simplified! We are essentially
        dropping the previously performed steps 2-4. It is in fact possible to
        make a WorldMap API delete layer call *by the datafile_id and the
        dataverse installation name*. And we already have these in the dict
        that we received from following the callback URL.
    (2) Try deleting the map layer and associated data on the WorldMap side
        (a new call has been added to the layer_services, that takes a dict, containing
        the datafile_id and dataverse_installation_name
    (3) And if that worked too, delete it locally, in GeoConnect.
    (4) Return 200 and a success message.
    """
    # ----------------------------------------------------
    # (1) Process the incoming url for a callback key 'cb'
    # and use the callback url to retrieve the DataverseInfo via a POST
    # (this is copied directly from the workflow of the "map-it" method)
    # ----------------------------------------------------
    request_helper = InitialRequestHelper(request, dataverse_token)
    if request_helper.has_err:
        user_err_msg = ('Failed to obtain datafile metadata'
                        ' from the Dataverse.'
                        ' Error: %s') % request_helper.err_msg
        return HttpResponse(\
                    MessageHelperJSON.get_json_fail_msg(user_err_msg),
                    status=412)

    dv_data_dict = request_helper.dv_data_dict

    # ----------------------------------------------------
    # (2) Try deleting the map layer and associated data on the WorldMap side
    # Note:
    # We dropped the "dv_data_dict['datafile_is_restricted'] is True" requirement
    # ----------------------------------------------------
    (success, err_msg) = delete_map_layer_by_cb_dict(request_helper.dv_data_dict)
    if success is False:
        LOGGER.error("Failed to delete WORLDMAP layer: %s", err_msg)
        return HttpResponse(\
                    MessageHelperJSON.get_json_fail_msg(\
                        "Failed to delete WorldMap layer: "+err_msg),
                    status=503)

    # ----------------------------------------------------
    # (3) Retrieve local GISDataFile objects and delete them.
    # This essentially clears all info about the layer and underlying datafile_id
    # e.g. GISDataFile is the superclass to ShapefileInfo, TabularInfo, etc
    #
    # Note: datafile_id and dataverse_installation_name have to be there--blow
    #       up if there's a key error
    # ----------------------------------------------------
    gis_data_kwargs = dict(\
        datafile_id=dv_data_dict['datafile_id'],
        dataverse_installation_name=dv_data_dict['dataverse_installation_name'])

    gis_data_objects = GISDataFile.objects.filter(**gis_data_kwargs)
    LOGGER.debug('gis_data_objects found: %s', gis_data_objects)

    if gis_data_objects.count() > 0:
        gis_data_objects.delete()

    # ----------------------------------------------------
    # (4) Success!
    # ----------------------------------------------------
    json_msg = MessageHelperJSON.get_json_success_msg(\
                    msg=('Successfully deleted WorldMap layer for the %s'
                         ' file, (datafile_id: %s)') %\
                            (request_helper.mapping_type,
                             dv_data_dict['datafile_id']))

    return HttpResponse(json_msg, content_type="application/json", status=200)
