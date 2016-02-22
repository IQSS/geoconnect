"""
Tabular views for:
    - Initial viewing of a Dataverse tabular file
    - Retrieval of Join Target Information including
        - Available geospatial types
        - Available geospatial layers
"""
from django.shortcuts import render_to_response

from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.template.loader import render_to_string

from apps.gis_tabular.models import TabularFileInfo # for testing
from apps.gis_tabular.models import TabularFileInfo,\
                    WorldMapJoinLayerInfo, WorldMapLatLngInfo
from apps.gis_tabular.forms import LatLngColumnsForm, ChooseSingleColumnForm
from apps.gis_tabular.tabular_helper import TabFileStats, NUM_PREVIEW_ROWS

from apps.worldmap_connect.utils import get_latest_jointarget_information,\
        get_geocode_types_and_join_layers

from geo_utils.message_helper_json import MessageHelperJSON

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
        # If available grab the first WorldMapJoinLayerInfo object
        worldmap_info = WorldMapJoinLayerInfo.objects.first()

    if worldmap_info is None:
        # If available grab the first WorldMapLatLngInfo object
        worldmap_info = WorldMapLatLngInfo.objects.first()

    if worldmap_info is None:
        return HttpResponse('Sorry! No WorldMapTabularLayerInfo objects available')

    tmpl_dict = dict(worldmap_layerinfo=worldmap_info,\
            layer_data=worldmap_info.core_data,\
            download_links=worldmap_info.download_links,\
            attribute_data=worldmap_info.attribute_data,\
            # for testing:
            tabular_info=worldmap_info.tabular_info,\
            test_files=TabularFileInfo.objects.all(),\
            )

    return render_to_response('gis_tabular/view_tabular_map.html',\
                            tmpl_dict,\
                            context_instance=RequestContext(request))



def build_tabular_map_html(request, worldmap_info):
    """
    Expects a WorldMapJoinLayerInfo or WorldMapLatLngInfo object

    Create HTML string displaying:
        - Completed map via iframe
        - Download links using Geoserver functions
        - Attribute table
    """
    if not (isinstance(worldmap_info, WorldMapJoinLayerInfo) and\
        isinstance(worldmap_info, WorldMapLatLngInfo)):
        return None

    d = dict(worldmap_layerinfo=worldmap_info,\
            layer_data=worldmap_info.core_data,\
            download_links=worldmap_info.download_links,\
            attribute_data=worldmap_info.attribute_data\
            )

    return render_to_string('gis_tabular/view_tabular_map_div.html',
                            d,
                            context_instance=RequestContext(request))

def view_tabular_file_first_time(request, tab_md5):
    """
    View tabular file that has been sent over via Dataverse
    """
    # ----------------------------------
    # Retrieve the Tabular file information
    # ----------------------------------
    try:
        tabular_info = TabularFileInfo.objects.get(md5=tab_md5)
    except TabularFileInfo.DoesNotExist:
        raise Http404('No TabularFileInfo for md5: %s' % tab_md5)

    return HttpResponse('Found tabular info: %s' % tab_md5)


def view_tabular_file_latest(request):

    tabular_info = TabularFileInfo.objects.first()
    if tabular_info is None:
        return HttpResponse('Sorry, no TabularFileInfo objects found')

    return view_tabular_file(request, tabular_info.id)


def view_tabular_file(request, tab_md5):
    """
    View tabular file that has been sent over via Dataverse
    """
    # ----------------------------------
    # Retrieve the Tabular file information
    # ----------------------------------
    try:
        tabular_info = TabularFileInfo.objects.get(md5=tab_md5)
    except TabularFileInfo.DoesNotExist:
        raise Http404('No TabularFileInfo for md5: %s' % tab_md5)


    # ----------------------------------
    # Does the file already have an associated layer
    # ----------------------------------
    worldmap_tabularinfo = tabular_info.get_worldmap_info()
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
    geocode_type_list = [(GEO_TYPE_LATITUDE_LONGITUDE, u'Latitude/Longitude')]

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
        form_single_column = ChooseSingleColumnForm(\
                    tabular_file_info_id=tabular_info.id,\
                    layer_choices=available_layers_list,\
                    column_names=tab_file_stats.column_names)
    else:
        form_single_column = None

    # ----------------------------------
    # Create a form for Lat/Lng column selection
    # ----------------------------------
    if tab_file_stats:
        form_lat_lng = LatLngColumnsForm(tabular_file_info_id=tabular_info.id,\
                    column_names=tab_file_stats.column_names)
    else:
        form_lat_lng = None

    template_dict = dict(tabular_id=tabular_info.id,\
            tabular_md5=tabular_info.md5,\
            tabular_info=tabular_info,\
            tab_file_stats=tab_file_stats,\
            geocode_types=geocode_type_list,\
            NUM_PREVIEW_ROWS=num_preview_rows,\
            test_files=TabularFileInfo.objects.all(),\
            form_single_column=form_single_column,\
            form_lat_lng=form_lat_lng,\
            GEO_TYPE_LATITUDE_LONGITUDE=GEO_TYPE_LATITUDE_LONGITUDE)

    return render_to_response('gis_tabular/view_tabular_overview.html',\
                            template_dict,\
                            context_instance=RequestContext(request))


def ajax_get_all_join_targets(request):
    """
    Calling "ajax_get_join_targets" without a selected_geo_type
    returns all available join targets
    """
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
