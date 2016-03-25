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
from django.conf import settings


from apps.gis_tabular.models import TabularFileInfo # for testing
from apps.gis_tabular.models import TabularFileInfo,\
                    WorldMapJoinLayerInfo, WorldMapLatLngInfo
from apps.gis_tabular.forms import LatLngColumnsForm, ChooseSingleColumnForm
from apps.gis_tabular.tabular_helper import TabFileStats, NUM_PREVIEW_ROWS
from apps.gis_tabular.forms_delete import DeleteTabularMapForm

from apps.worldmap_connect.utils import get_latest_jointarget_information,\
        get_geocode_types_and_join_layers

from geo_utils.geoconnect_step_names import GEOCONNECT_STEP_KEY,\
    GEOCONNECT_STEPS, STEP1_EXAMINE, STEP3_STYLE
from geo_utils.view_util import get_common_lookup

from geo_utils.message_helper_json import MessageHelperJSON

from apps.gis_tabular.forms import GEO_TYPE_LATITUDE_LONGITUDE

from shared_dataverse_information.layer_classification.forms import\
    ClassifyLayerForm, ATTRIBUTE_VALUE_DELIMITER

from apps.gis_tabular.tab_services import add_worldmap_layerinfo_if_exists
from apps.gis_basic_file.views import render_breadcrumb_div_for_style_step,\
    render_main_panel_title_for_style_step

#from geo_utils.msg_util import *
#from geo_utils.geoconnect_step_names import GEOCONNECT_STEP_KEY, STEP1_EXAMINE
#from apps.gis_shapefiles.shp_services import get_shapefile_from_dv_api_info
#from geo_utils.view_util import get_common_lookup

import logging
LOGGER = logging.getLogger(__name__)


def view_existing_map(request, worldmap_info=None):
    """
    Test view a WorldMapTabularLayerInfo object
    """
    if not (isinstance(worldmap_info, WorldMapJoinLayerInfo) or\
        isinstance(worldmap_info, WorldMapLatLngInfo)):
        LOGGER.error('worldmap_info needs to be a WorldMapJoinLayerInfo\
         or WorldMapLatLngInfo object. Not: %s', worldmap_info)
        return HttpResponse('Sorry! No WorldMap information was found.')

    template_dict = get_common_lookup(request)

    main_panel_title = render_main_panel_title_for_style_step(worldmap_info.tabular_info)

    template_dict = dict(worldmap_layerinfo=worldmap_info,\
        attribute_data=worldmap_info.attribute_data,\
        tabular_map_div=build_tabular_map_html(request, worldmap_info),\
        tabular_info=worldmap_info.tabular_info,\
        #id_main_panel_title=main_panel_title,\
        #id_breadcrumb=render_breadcrumb_div_for_style_step(),\
        # for testing
        test_files=TabularFileInfo.objects.all(),\
        )

    template_dict[GEOCONNECT_STEP_KEY] = STEP3_STYLE
    template_dict['GEOCONNECT_STEPS'] = GEOCONNECT_STEPS

    return render_to_response('gis_tabular/view_tabular_map.html',\
                            template_dict,\
                            context_instance=RequestContext(request))



def build_tabular_map_html(request, worldmap_info):
    """
    Expects a WorldMapJoinLayerInfo or WorldMapLatLngInfo object

    Create HTML string displaying:
        - Completed map via iframe
        - Download links using Geoserver functions
        - User message about join
        - Attribute table
    """
    if not (isinstance(worldmap_info, WorldMapJoinLayerInfo) or\
        isinstance(worldmap_info, WorldMapLatLngInfo)):
        LOGGER.error('worldmap_info needs to be a WorldMapJoinLayerInfo\
         or WorldMapLatLngInfo object. Not: %s', worldmap_info)
        return None

    delete_form = DeleteTabularMapForm.get_form_with_initial_vals(worldmap_info)

    template_dict = get_common_lookup(request)

    template_dict.update(dict(worldmap_layerinfo=worldmap_info,\
            core_data=worldmap_info.core_data,\
            tabular_info=worldmap_info.tabular_info,\
            download_links=worldmap_info.download_links,\
            attribute_data=worldmap_info.attribute_data,\
            delete_form=delete_form,\
            is_tabular_delete=True,\
            ))

    # --------------------------------
    # Classification form attributes
    # --------------------------------
    classify_params = {GEOCONNECT_STEP_KEY : STEP3_STYLE,\
            'ATTRIBUTE_VALUE_DELIMITER' : ATTRIBUTE_VALUE_DELIMITER,\
            'classify_form' : ClassifyLayerForm(\
                **worldmap_info.get_dict_for_classify_form())}

    template_dict.update(classify_params)

    return render_to_string('gis_tabular/view_tabular_map_div.html',\
                            template_dict,\
                            context_instance=RequestContext(request))


def view_unmatched_join_rows(request, tab_md5):
    """
    View the unmatched rows resulting from a Table Join
    """
    # ----------------------------------
    # Retrieve the Tabular file information
    # ----------------------------------
    try:
        worldmap_info = WorldMapJoinLayerInfo.objects.get(md5=tab_md5)
    except WorldMapJoinLayerInfo.DoesNotExist:
        raise Http404('No WorldMapJoinLayerInfo for md5: %s' % tab_md5)

    if worldmap_info.core_data and\
        'unmatched_records_list' in worldmap_info.core_data:
        # Unmatched records exist

        json_msg = MessageHelperJSON.get_json_msg(success=True,\
                        msg="Records found",\
                        data_dict=worldmap_info.core_data['unmatched_records_list'])
    else:
        # No unmatched records exist
        json_msg = MessageHelperJSON.get_json_msg(success=False,\
                        msg="No unmatched records found.")

    return HttpResponse(json_msg, content_type="application/json")

def view_unmatched_lat_lng_rows(request, tab_md5):
    """
    View the unmatched rows resulting from a Table Join
    """
    # ----------------------------------
    # Retrieve the Tabular file information
    # ----------------------------------
    try:
        worldmap_info = WorldMapLatLngInfo.objects.get(md5=tab_md5)
    except WorldMapLatLngInfo.DoesNotExist:
        raise Http404('No WorldMapLatLngInfo for md5: %s' % tab_md5)

    if worldmap_info.core_data and\
        'unmapped_records_list' in worldmap_info.core_data:
        # Unmatched records exist

        unmatched_rows_html = render_to_string('gis_tabular/unmatched_rows.html',\
            dict(ummatched_rows=worldmap_info.core_data['unmapped_records_list'],\
                column_names=worldmap_info.attribute_data,
            ),\
            context_instance=RequestContext(request))

        return HttpResponse(unmatched_rows_html)
        json_msg = MessageHelperJSON.get_json_msg(success=True,\
                        msg="Records found",\
                        data_dict=worldmap_info.core_data['unmapped_records_list'])
    else:
        # No unmatched records exist
        json_msg = MessageHelperJSON.get_json_msg(success=False,\
                        msg="No unmatched records found.")


    #from django.template.loader import render_to_string

    return HttpResponse(json_msg, content_type="application/json")


def view_tabular_file_latest(request):

    tabular_info = TabularFileInfo.objects.first()
    if tabular_info is None:
        return HttpResponse('Sorry, no TabularFileInfo objects found')

    return view_tabular_file(request, tabular_info.md5)


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
        return view_existing_map(request, worldmap_tabularinfo)

    #
    # Is there a WorldMap layer but Geoconnect doesn't know about it?
    #
    if add_worldmap_layerinfo_if_exists(tabular_info):
        worldmap_tabularinfo = tabular_info.get_worldmap_info()
        if worldmap_tabularinfo:
            return view_existing_map(request, worldmap_tabularinfo)


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

    template_dict = get_common_lookup(request)

    template_dict.update(dict(tabular_id=tabular_info.id,\
            tabular_md5=tabular_info.md5,\
            tabular_info=tabular_info,\
            tab_file_stats=tab_file_stats,\
            geocode_types=geocode_type_list,\
            NUM_PREVIEW_ROWS=num_preview_rows,\
            test_files=TabularFileInfo.objects.all(),\
            form_single_column=form_single_column,\
            form_lat_lng=form_lat_lng,\
            GEO_TYPE_LATITUDE_LONGITUDE=GEO_TYPE_LATITUDE_LONGITUDE))

    template_dict[GEOCONNECT_STEP_KEY] = STEP1_EXAMINE
    template_dict['GEOCONNECT_STEPS'] = GEOCONNECT_STEPS

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
