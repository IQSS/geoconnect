from django.shortcuts import render_to_response

from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string

from django.conf import settings

from django.views.decorators.http import require_POST

from apps.gis_tabular.models import SimpleTabularTest # for testing
from apps.gis_tabular.models import WorldMapTabularLayerInfo
from apps.gis_tabular.forms import LatLngColumnsForm, ChooseSingleColumnForm
from apps.gis_tabular.tabular_helper import TabFileStats, NUM_PREVIEW_ROWS

from apps.worldmap_connect.utils import get_latest_jointarget_information, get_geocode_types_and_join_layers

from geo_utils.message_helper_json import MessageHelperJSON, format_errors_as_text

from apps.worldmap_connect.lat_lng_service import create_map_from_datatable_lat_lng
from apps.worldmap_connect.join_layer_service import create_map_from_datatable_join

from apps.gis_tabular.dataverse_test_info import DataverseTestInfo
from apps.gis_tabular.forms import GEO_TYPE_LATITUDE_LONGITUDE
#from geo_utils.msg_util import *
#from geo_utils.geoconnect_step_names import GEOCONNECT_STEP_KEY, STEP1_EXAMINE
#from apps.gis_shapefiles.shp_services import get_shapefile_from_dv_api_info
#from geo_utils.view_util import get_common_lookup

import logging
LOGGER = logging.getLogger(__name__)


def view_sample_map(request, worldmap_info=None):
    """
    Test view a WorldMapTabularLayerInfo object
    """
    if worldmap_info is None:
        worldmap_info = WorldMapTabularLayerInfo.objects.first()

    if worldmap_info is None:
        return HttpResponse('Sorry! No WorldMapTabularLayerInfo objects available')

    d = dict(worldmap_layerinfo=worldmap_info,
            layer_data=worldmap_info.core_data,
            download_links=worldmap_info.download_links,
            attribute_data=worldmap_info.attribute_data,
            # for testing:
            tabular_info=worldmap_info.tabular_info,
            test_files=SimpleTabularTest.objects.all(),
            )

    return render_to_response('gis_tabular/view_tabular_map.html',
                            d,
                            context_instance=RequestContext(request))



def build_tabular_map_html(request, worldmap_info):
    if not isinstance(worldmap_info, WorldMapTabularLayerInfo):
        return None

    d = dict(worldmap_layerinfo=worldmap_info,
            layer_data=worldmap_info.core_data,
            download_links=worldmap_info.download_links,
            attribute_data=worldmap_info.attribute_data
            )

    return render_to_string('gis_tabular/view_tabular_map_div.html',
                            d,
                            context_instance=RequestContext(request))



@require_POST
def view_map_tabular_file_form(request):
    """
    Join your tabular file to a WorldMap layer
    using the column selected in this form
    """
    for k, v in request.POST.items():
        print k, v

    tabular_file_info_id = request.POST.get('tabular_file_info_id', -1)

    try:
        tabular_info = SimpleTabularTest.objects.get(pk=tabular_file_info_id)
    except SimpleTabularTest.DoesNotExist:
        err_msg = 'Sorry! The Tabular File was not found. (tabular_file_info_id)'
        json_msg = MessageHelperJSON.get_json_fail_msg(err_msg)
        return HttpResponse(json_msg, mimetype="application/json", status=200)
        #raise Http404('No SimpleTabularTest for id: %s' % tabular_file_info_id)



    # Retrieve available Geocode types and join Layers
    (geocode_types_from_worldmap, available_layers_list) = get_geocode_types_and_join_layers()

    # Create form with initial + POST data
    form_single_column = ChooseSingleColumnForm(tabular_info.id,
                    available_layers_list,
                    tabular_info.column_names,
                    request.POST)

    if not form_single_column.is_valid():
        json_msg = MessageHelperJSON.get_json_fail_msg(\
                        format_errors_as_text(form_single_column, for_web=True))
        return HttpResponse(json_msg, mimetype="application/json", status=200)

    print 'cleaned_data', form_single_column.cleaned_data

    dataverse_metadata_dict = DataverseTestInfo.get_dataverse_test_info_dict(
                    tabular_info.name,
                    tabular_info.dv_file.path)


    (success, worldmap_data_or_err_msg) = create_map_from_datatable_join(tabular_info,
                        dataverse_metadata_dict,
                        form_single_column.cleaned_data.get('chosen_column'),
                        form_single_column.cleaned_data.get('chosen_layer'),
                        )
    print '-' * 40
    print 'success', success
    print 'worldmap_data_or_err_msg', worldmap_data_or_err_msg
    print '-' * 40

    # -----------------------------------------
    # Failed! Return error message
    # -----------------------------------------
    if not success:
        json_msg = MessageHelperJSON.get_json_fail_msg('Sorry! ' + worldmap_data_or_err_msg)
        return HttpResponse(json_msg, mimetype="application/json", status=200)

    # -----------------------------------------
    # Succeeded!  Create a WorldMapTabularLayerInfo object
    # -----------------------------------------
    worldmap_tabular_info = WorldMapTabularLayerInfo.build_from_worldmap_json(tabular_info,
                                worldmap_data_or_err_msg)

    if worldmap_tabular_info is None:
        LOGGER.error("Failed to create WorldMapTabularLayerInfo using %s" , worldmap_data_or_err_msg)
        user_msg = 'Sorry! Failed to create map. Please try again. (code: s1)'
        json_msg = MessageHelperJSON.get_json_fail_msg(user_msg)
        return HttpResponse(json_msg, mimetype="application/json", status=200)

    # -----------------------------------------
    # Build the Map HTML chunk to replace the form
    # -----------------------------------------
    map_html = build_tabular_map_html(request, worldmap_tabular_info)
    if map_html is None:
        LOGGER.error("Failed to create map HTML using WorldMapTabularLayerInfo: %s (%d)" ,
            worldmap_tabular_info, worldmap_tabular_info.id)
        user_msg = 'Sorry! Failed to create map. Please try again. (code: s2)'
        json_msg = MessageHelperJSON.get_json_fail_msg(user_msg)
        return HttpResponse(json_msg, mimetype="application/json", status=200)

    #    msg, response_data = worldmap_msg
    data_dict = dict(map_html=map_html)
    json_msg = MessageHelperJSON.get_json_success_msg("great job", data_dict=data_dict)

    return HttpResponse(json_msg, mimetype="application/json", status=200)

    #json_msg = MessageHelperJSON.get_json_success_msg('You got here! (view_map_tabular_file_form)')
    #return HttpResponse(json_msg, mimetype="application/json", status=200)




@require_POST
def view_process_lat_lng_column_form(request):
    """
    Create a WorldMap layer from your tabular file
    using the latitude and longitude columns selected in this form
    """

    tabular_file_info_id = request.POST.get('tabular_file_info_id', -1)

    try:
        tabular_info = SimpleTabularTest.objects.get(pk=tabular_file_info_id)
    except SimpleTabularTest.DoesNotExist:
        err_msg = 'Sorry! The Tabular File was not found. (tabular_file_info_id)'
        json_msg = MessageHelperJSON.get_json_fail_msg(err_msg)
        return HttpResponse(json_msg, mimetype="application/json", status=200)
        #raise Http404('No SimpleTabularTest for id: %s' % tabular_file_info_id)

    f = LatLngColumnsForm(tabular_info.id, tabular_info.column_names, request.POST)
    if not f.is_valid():
        json_msg = MessageHelperJSON.get_json_fail_msg(format_errors_as_text(f, for_web=True))
        #json_msg = MessageHelperJSON.get_json_fail_msg(f.err_msg_for_web)
        return HttpResponse(json_msg, mimetype="application/json", status=200)

        #print f.errors.items()
        #print 'Type: ', type(f)
        #print dir(f)#'Type: ', type(f)
        #print 'f.is_valid(): %s' % f.is_valid()

    dataverse_metadata_dict = DataverseTestInfo.get_dataverse_test_info_dict(
                        tabular_info.name,
                        tabular_info.dv_file.path)

    (success, worldmap_msg) = create_map_from_datatable_lat_lng(tabular_info,
                        dataverse_metadata_dict,
                        f.get_latitude_colname(),
                        f.get_longitude_colname(),
                        )

    if success:
        msg, response_data = worldmap_msg
        json_msg = MessageHelperJSON.get_json_success_msg(worldmap_msg, data_dict=response_data)
    else:
        json_msg = MessageHelperJSON.get_json_fail_msg('Sorry! ' + worldmap_msg)

    return HttpResponse(json_msg, mimetype="application/json", status=200)


def view_test_file(request, tabular_id):

    # ----------------------------------
    # Retrieve the Tabular file information
    # ----------------------------------
    try:
        tabular_info = SimpleTabularTest.objects.get(pk=tabular_id)
    except SimpleTabularTest.DoesNotExist:
        raise Http404('No SimpleTabularTest for id: %s' % tabular_id)


    # ----------------------------------
    # Does the file already have an associated layer
    # ----------------------------------
    worldmap_tabularinfo = tabular_info.worldmaptabularlayerinfo_set.first()
    if worldmap_tabularinfo is not None:
        # A map exists: show it!
        return view_sample_map(request, worldmap_tabularinfo)

    # ----------------------------------
    # Open the file and get the stats
    # ----------------------------------
    tab_file_stats = TabFileStats.create_tab_stats_from_tabular_info(tabular_info)
    # preview rows
    num_preview_rows = min([x for x in (NUM_PREVIEW_ROWS, tabular_info.num_rows) if x > 0])

    # ----------------------------------
    # Format values for geospatial data type dropdown
    # ----------------------------------
    # Always include lat/lng as a dropdown choice
    geocode_type_list = [( GEO_TYPE_LATITUDE_LONGITUDE, u'Latitude/Longitude')]

    # Retrieve available Geocode types and join Layers
    (geocode_types_from_worldmap, available_layers_list) = get_geocode_types_and_join_layers()

    # Add WorldMap join targets (if any)
    if geocode_types_from_worldmap:
        geocode_type_list += geocode_types_from_worldmap

    # Separate list of all join layers (which are filtered by type on form)
    print 'available_layers_list', available_layers_list
    # ----------------------------------
    # Create a Django form for table join column selection
    # ----------------------------------
    if available_layers_list and len(available_layers_list) > 0:
        form_single_column = ChooseSingleColumnForm(tabular_file_info_id=tabular_info.id,
                    layer_choices=available_layers_list,
                    column_names=tab_file_stats.column_names)
    else:
        form_single_column = None

    # ----------------------------------
    # Create a form for Lat/Lng column selection
    # ----------------------------------
    if tab_file_stats:
        form_lat_lng = LatLngColumnsForm(tabular_file_info_id=tabular_info.id,
                    column_names=tab_file_stats.column_names)
    else:
        form_lat_lng = None

    d = dict(tabular_id=tabular_id,\
            tabular_info=tabular_info,\
            tab_file_stats=tab_file_stats,\
            geocode_types=geocode_type_list,\
            NUM_PREVIEW_ROWS=num_preview_rows,\
            test_files=SimpleTabularTest.objects.all(),\
            form_single_column=form_single_column,\
            form_lat_lng=form_lat_lng,\
            GEO_TYPE_LATITUDE_LONGITUDE=GEO_TYPE_LATITUDE_LONGITUDE)

    return render_to_response('gis_tabular/view_test_file.html', d\
                                     , context_instance=RequestContext(request))




def ajax_get_all_join_targets(request):

    return ajax_get_join_targets(request, None)


def ajax_get_join_targets(request, selected_geo_type):
    """
    Ajax - Retrieve JoinTarget information that matches
            a selected geospatial identification type

    Returns a list for use in loading a dropdown box
    """
    jt = get_latest_jointarget_information()

    join_target_info = jt.get_available_layers_list_by_type(selected_geo_type)
    if join_target_info is None:
        err_msg = "Sorry! No Join Targets found for Geospatial type: {0}".format(selected_geo_type)
        json_msg = MessageHelperJSON.get_json_msg(success=False,\
                                msg=err_msg)
        return HttpResponse(status=400, content=json_msg, content_type="application/json")


    json_msg = MessageHelperJSON.get_json_msg(success=True,\
                                msg="success",\
                                data_dict=join_target_info)

    return HttpResponse(status=200, content=json_msg, content_type="application/json")
