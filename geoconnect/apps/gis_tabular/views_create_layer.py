"""
Views to create WorldMap layers by:
    - Joining a tabular file to an existing layer OR
    - Using Lat/Lng columns for mapping
"""
from django.http import HttpResponse

from django.views.decorators.http import require_POST
from apps.gis_tabular.models import TabularFileInfo # for testing
from apps.gis_tabular.models import WorldMapTabularLayerInfo
from apps.gis_tabular.forms import LatLngColumnsForm, ChooseSingleColumnForm

from apps.worldmap_connect.utils import get_geocode_types_and_join_layers

from geo_utils.message_helper_json import MessageHelperJSON, format_errors_as_text

from apps.worldmap_connect.lat_lng_service import create_map_from_datatable_lat_lng
from apps.worldmap_connect.table_join_map_maker import TableJoinMapMaker

from apps.gis_tabular.dataverse_test_info import DataverseTestInfo
from apps.gis_tabular.views import build_tabular_map_html

from geo_utils.msg_util import msg, msgt

import logging
LOGGER = logging.getLogger(__name__)


@require_POST
def view_map_tabular_file_form(request):
    """
    Join your tabular file to a WorldMap layer
    using the column selected in this form
    """
    #for k, v in request.POST.items():
    #        print k, v

    # -----------------------------------------
    # Retrieve the id of the Tabular info object
    # -----------------------------------------
    tabular_file_info_id = request.POST.get('tabular_file_info_id', -1)

    try:
        tabular_info = TabularFileInfo.objects.get(pk=tabular_file_info_id)
    except TabularFileInfo.DoesNotExist:
        err_msg = 'Sorry! The Tabular File was not found. (tabular_file_info_id)'
        json_msg = MessageHelperJSON.get_json_fail_msg(err_msg)
        return HttpResponse(json_msg, mimetype="application/json", status=200)
        #raise Http404('No TabularFileInfo for id: %s' % tabular_file_info_id)

    # -----------------------------------------
    # Retrieve available Geocode types and join Layers
    #   note: geocode_types_from_worldmap not needed here
    # -----------------------------------------
    (geocode_types_from_worldmap, available_layers_list) = get_geocode_types_and_join_layers()

    # -----------------------------------------
    # Create form with initial + POST data
    # -----------------------------------------
    form_single_column = ChooseSingleColumnForm(tabular_info.id,\
                    available_layers_list,\
                    tabular_info.column_names,\
                    request.POST)

    # -----------------------------------------
    # Check the form's validity
    # -----------------------------------------
    if not form_single_column.is_valid():
        json_msg = MessageHelperJSON.get_json_fail_msg(\
                        format_errors_as_text(form_single_column, for_web=True))
        return HttpResponse(json_msg, mimetype="application/json", status=200)

    print 'cleaned_data', form_single_column.cleaned_data

    # -----------------------------------------
    # Get Dataverse info dict
    # -----------------------------------------
    dataverse_metadata_dict = DataverseTestInfo.get_dataverse_test_info_dict(\
                    tabular_info.name,\
                    tabular_info.dv_file.path)

    # -----------------------------------------
    # Use the WorldMap API and
    # try to create a layer
    # -----------------------------------------
    tj_map_maker = TableJoinMapMaker(tabular_info,\
                        dataverse_metadata_dict,\
                        form_single_column.cleaned_data.get('chosen_column'),\
                        form_single_column.cleaned_data.get('chosen_layer'),\
                        )
    success = tj_map_maker.run_map_create()
    msg('success: %s' % success)
    if not success:
        json_msg = MessageHelperJSON.get_json_fail_msg(\
                    'Sorry! ' + tj_map_maker.get_error_msg())
        msg('error msg: %s' % json_msg)
        return HttpResponse(json_msg, mimetype="application/json", status=200)


    # -----------------------------------------
    # Succeeded!  Create a WorldMapTabularLayerInfo object
    # -----------------------------------------
    worldmap_tabular_info = WorldMapTabularLayerInfo.build_from_worldmap_json(tabular_info,\
                                tj_map_maker.get_map_info())


    if worldmap_tabular_info is None:
        LOGGER.error("Failed to create WorldMapTabularLayerInfo using %s",\
            tj_map_maker.get_map_info())
        user_msg = 'Sorry! Failed to create map. Please try again. (code: s1)'
        json_msg = MessageHelperJSON.get_json_fail_msg(user_msg)
        return HttpResponse(json_msg, mimetype="application/json", status=200)

    # -----------------------------------------
    # Build the Map HTML chunk to replace the form
    # -----------------------------------------
    map_html = build_tabular_map_html(request, worldmap_tabular_info)
    if map_html is None:    # Failed!  Send an error
        LOGGER.error("Failed to create map HTML using WorldMapTabularLayerInfo: %s (%d)",\
            worldmap_tabular_info, worldmap_tabular_info.id)
        user_msg = 'Sorry! Failed to create map. Please try again. (code: s2)'
        json_msg = MessageHelperJSON.get_json_fail_msg(user_msg)
        return HttpResponse(json_msg, mimetype="application/json", status=200)

    # -----------------------------------------
    # Looks good.  In the JSON response, send
    #   back the map HTML
    # -----------------------------------------
    data_dict = dict(map_html=map_html)
    json_msg = MessageHelperJSON.get_json_success_msg("great job", data_dict=data_dict)

    return HttpResponse(json_msg, mimetype="application/json", status=200)

    #json_msg = MessageHelperJSON.get_json_success_msg('You got here! (view_map_tabular_file_form)')
    #return HttpResponse(json_msg, mimetype="application/json", status=200)


@require_POST
def view_process_lat_lng_form(request):
    """
    Create a WorldMap layer from your tabular file
    using the latitude and longitude columns selected in this form
    """

    tabular_file_info_id = request.POST.get('tabular_file_info_id', -1)

    try:
        tabular_info = TabularFileInfo.objects.get(pk=tabular_file_info_id)
    except TabularFileInfo.DoesNotExist:
        err_msg = 'Sorry! The Tabular File was not found. (tabular_file_info_id)'
        json_msg = MessageHelperJSON.get_json_fail_msg(err_msg)
        return HttpResponse(json_msg, mimetype="application/json", status=200)
        #raise Http404('No TabularFileInfo for id: %s' % tabular_file_info_id)

    form_lat_lng = LatLngColumnsForm(tabular_info.id,\
                        tabular_info.column_names,\
                        request.POST)
    if not form_lat_lng.is_valid():
        json_msg = MessageHelperJSON.get_json_fail_msg(\
                    format_errors_as_text(form_lat_lng,\
                                        for_web=True)\
                                    )
        #json_msg = MessageHelperJSON.get_json_fail_msg(f.err_msg_for_web)
        return HttpResponse(json_msg, mimetype="application/json", status=200)


    (success, worldmap_data_or_err_msg) = create_map_from_datatable_lat_lng(\
                        tabular_info,\
                        form_lat_lng.get_latitude_colname(),\
                        form_lat_lng.get_longitude_colname(),\
                        )

    # -----------------------------------------
    # Failed! Send error message
    # -----------------------------------------
    if not success:
        json_msg = MessageHelperJSON.get_json_fail_msg(\
                'Sorry! ' + worldmap_data_or_err_msg)
        return HttpResponse(json_msg, mimetype="application/json", status=200)


    # -----------------------------------------
    # Succeeded!  Create a WorldMapTabularLayerInfo object
    # -----------------------------------------
    user_msg, response_data = worldmap_data_or_err_msg
    #json_msg = MessageHelperJSON.get_json_success_msg(user_msg, data_dict=response_data)
    #return HttpResponse(json_msg, mimetype="application/json", status=200)

    worldmap_latlng_info = WorldMapTabularLayerInfo.build_from_worldmap_json(tabular_info,\
                            response_data)

    if worldmap_latlng_info is None:
        LOGGER.error("Failed to create WorldMapLatLngInfo using data: %s",\
                    response_data)
        user_msg = 'Sorry! Failed to create map. Please try again. (code: s4)'
        json_msg = MessageHelperJSON.get_json_fail_msg(user_msg)
        return HttpResponse(json_msg, mimetype="application/json", status=200)

    # -----------------------------------------
    # Possible that this failed.
    # Make sure at least 1 row mapped
    # -----------------------------------------
    # Skip for now!  Error in row counts for Lat/Lng!
    """
    if worldmap_latlng_info.did_any_rows_map() is False:
        # Delete the worldmap_latlng_info object
        worldmap_latlng_info.delete()

        # Send back a user error message
        user_msg = "Sorry!  We couldn't map any of those latitude and longitude values."
        return HttpResponse(MessageHelperJSON.get_json_fail_msg(user_msg),\
                mimetype="application/json",\
                status=200)
    """
    # -----------------------------------------
    # Build the Map HTML chunk to replace the form
    # -----------------------------------------
    map_html = build_tabular_map_html(request, worldmap_latlng_info)
    if map_html is None:    # Failed!  Send an error
        LOGGER.error("Failed to create map HTML using WorldMapLatLngInfo: %s (%d)",\
            worldmap_latlng_info, worldmap_latlng_info.id)
        user_msg = 'Sorry! Failed to create map. Please try again. (code: s5)'
        json_msg = MessageHelperJSON.get_json_fail_msg(user_msg)
        return HttpResponse(json_msg, mimetype="application/json", status=200)


    # -----------------------------------------
    # Looks good.  In the JSON response, send
    #   back the map HTML
    # -----------------------------------------
    data_dict = dict(map_html=map_html)
    json_msg = MessageHelperJSON.get_json_success_msg("great job", data_dict=data_dict)

    return HttpResponse(json_msg, mimetype="application/json", status=200)
