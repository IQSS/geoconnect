"""
Tabular views for:
    - Initial viewing of a Dataverse tabular file
    - Retrieval of Join Target Information including
        - Available geospatial types
        - Available geospatial layers
"""
import csv

from django.shortcuts import render

from django.http import HttpResponse, Http404
from django.template.loader import render_to_string

from gc_apps.gis_tabular.models import TabularFileInfo,\
                    WorldMapJoinLayerInfo, WorldMapLatLngInfo
from gc_apps.gis_tabular.unmapped_row_util import UnmatchedRowHelper

from gc_apps.gis_tabular.forms import LatLngColumnsForm, ChooseSingleColumnForm,\
    SELECT_LABEL, INITIAL_SELECT_CHOICE
from gc_apps.gis_tabular.tab_file_stats import TabFileStats, NUM_PREVIEW_ROWS
from gc_apps.gis_tabular.forms_delete import DeleteMapForm

from gc_apps.worldmap_layers.models import WorldMapLayerInfo

from gc_apps.worldmap_connect.utils import get_latest_jointarget_information,\
        get_geocode_types_and_join_layers
from gc_apps.gis_tabular.unmapped_row_util import MAX_FAILED_ROWS_TO_BUILD

from gc_apps.geo_utils.geoconnect_step_names import GEOCONNECT_STEP_KEY,\
    GEOCONNECT_STEPS, STEP1_EXAMINE, STEP2_STYLE,\
    PANEL_TITLE_MAP_DATA_FILE, PANEL_TITLE_STYLE_MAP
from gc_apps.geo_utils.view_util import get_common_lookup

from gc_apps.geo_utils.message_helper_json import MessageHelperJSON
from gc_apps.geo_utils.time_util import get_datetime_string_for_file

from gc_apps.gis_tabular.forms import GEO_TYPE_LATITUDE_LONGITUDE

from shared_dataverse_information.layer_classification.forms import\
    ClassifyLayerForm, ATTRIBUTE_VALUE_DELIMITER

from gc_apps.gis_tabular.tab_services import add_worldmap_layerinfo_if_exists

import logging
LOGGER = logging.getLogger(__name__)


def view_existing_map(request, worldmap_info=None):
    """
    View a WorldMapTabularLayerInfo object
    """
    if not (isinstance(worldmap_info, WorldMapJoinLayerInfo) or\
        isinstance(worldmap_info, WorldMapLatLngInfo)):
        LOGGER.error('worldmap_info needs to be a WorldMapJoinLayerInfo\
         or WorldMapLatLngInfo object. Not: %s', worldmap_info)
        return HttpResponse('Sorry! No WorldMap information was found.')

    template_dict = get_common_lookup(request)

    map_html, user_message_html = build_map_html(request, worldmap_info)
    if map_html is None:
        LOGGER.error("Failed to create map HTML using worldmap_info: %s (%d)" %\
            worldmap_info, worldmap_info.id)
        user_msg = 'Sorry! Failed to create map. Please try again. (code:ve3)'
        return HttpResponse(user_msg)


    template_dict.update(\
        dict(worldmap_layerinfo=worldmap_info,
        attribute_data=worldmap_info.attribute_data,
        tabular_map_div=map_html,
        user_message_html=user_message_html,    # not used for existing maps
        gis_data_info=worldmap_info.get_gis_data_info(),
        test_files=TabularFileInfo.objects.all(),
        page_title=PANEL_TITLE_STYLE_MAP))

    template_dict[GEOCONNECT_STEP_KEY] = STEP2_STYLE
    template_dict['GEOCONNECT_STEPS'] = GEOCONNECT_STEPS

    return render(request, 'tabular_files/main_outline_tab.html', template_dict)



def build_map_html(request, worldmap_info):
    """
    Expects a WorldMapLayerInfo object

    Create 2 HTML strings:
        1 - map_html
            - Completed map via iframe
            - Download links using Geoserver functions
            - Attribute table
        2 - user_message_html
            - User message about join
    """
    if not isinstance(worldmap_info, WorldMapLayerInfo):
        err_msg = ('worldmap_info needs to be a WorldMapLayerInfo'
                   ' object. Not type: %s')\
                   % (type(worldmap_info))
        LOGGER.error(err_msg)
        return None, None

    delete_form = DeleteMapForm.get_form_with_initial_vals(worldmap_info)

    template_dict = get_common_lookup(request)

    failed_records_list = worldmap_info.get_failed_rows()
    num_failed_download_records = min(MAX_FAILED_ROWS_TO_BUILD,\
                            worldmap_info.get_unmapped_record_count())


    template_dict.update(dict(\
            worldmap_layerinfo=worldmap_info,
            INITIAL_SELECT_CHOICE=INITIAL_SELECT_CHOICE,
            SELECT_LABEL=SELECT_LABEL,
            core_data=worldmap_info.core_data,
            gis_data_info=worldmap_info.get_gis_data_info(),
            download_links=worldmap_info.get_formatted_download_links(),
            attribute_data=worldmap_info.attribute_data,
            failed_records_list=failed_records_list,
            num_failed_download_records=num_failed_download_records,
            delete_form=delete_form,
            page_title=PANEL_TITLE_STYLE_MAP))

    # --------------------------------
    # Classification form attributes
    # --------------------------------
    classify_form = ClassifyLayerForm(\
            **worldmap_info.get_dict_for_classify_form())

    classify_params = {\
            GEOCONNECT_STEP_KEY : STEP2_STYLE,\
            'ATTRIBUTE_VALUE_DELIMITER' : ATTRIBUTE_VALUE_DELIMITER,\
            'classify_form' : classify_form}

    template_dict.update(classify_params)

    map_html = render_to_string('worldmap_layers/map_with_classify.html',
                                template_dict,
                                request)

    user_message_html = render_to_string('worldmap_layers/new_map_message.html',
                                         template_dict,
                                         request)

    return (map_html, user_message_html)


def view_unmatched_join_rows_json(request, tab_md5):
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
        unmatched_row_dict = dict(
            ummatched_rows=worldmap_info.core_data.get('unmatched_records_list', None),
            column_names=worldmap_info.attribute_data)

        unmatched_rows_html = render_to_string('metadata/unmatched_records.html',
            unmatched_row_dict,
            request)

        return HttpResponse(unmatched_rows_html)

        json_msg = MessageHelperJSON.get_json_msg(\
                        success=True,
                        msg="Records found",
                        data_dict=worldmap_info.core_data['unmatched_rows'])
    else:
        # No unmatched records exist
        json_msg = MessageHelperJSON.get_json_msg(\
                        success=False,
                        msg="No unmatched records found.")

    return HttpResponse(json_msg, content_type="application/json")


def download_unmatched_join_rows(request, tab_md5):
    """Download the unmatched tabular *join* data in csv format"""
    # Retrieve the Tabular file information
    #
    try:
        worldmap_info = WorldMapJoinLayerInfo.objects.get(md5=tab_md5)
    except WorldMapJoinLayerInfo.DoesNotExist:
        raise Http404('No WorldMapJoinLayerInfo for md5: %s' % tab_md5)

    if worldmap_info.core_data and\
        'unmatched_records_list' in worldmap_info.core_data:
        pass    # we have some data...
    else:
        return HttpResponse("No unmatched records found.")


    kwargs = dict(show_all_failed_rows=True)
    unmatched_row_helper = UnmatchedRowHelper(worldmap_info, **kwargs)
    csv_string = unmatched_row_helper.get_failed_rows_as_csv()

    if unmatched_row_helper.has_error:
        return HttpResponse(unmatched_row_helper.error_message)

    response = HttpResponse(csv_string, content_type='text/csv')

    file_name = 'unmapped_rows__%s.csv' % (get_datetime_string_for_file())
    response['Content-Disposition'] = 'attachment; filename="%s"' % file_name

    return response

    #return HttpResponse(csv_string, content_type='text/csv')


def download_unmatched_lat_lng_rows(request, tab_md5):
    """Download the unmatched data in csv format"""

    # Retrieve the Tabular file information
    #
    try:
        worldmap_info = WorldMapLatLngInfo.objects.get(md5=tab_md5)
    except WorldMapLatLngInfo.DoesNotExist:
        raise Http404('No WorldMapLatLngInfo for md5: %s' % tab_md5)

    if worldmap_info.core_data and\
        'unmapped_records_list' in worldmap_info.core_data:
        pass    # we have some data...
    else:
        return HttpResponse("No unmatched records found.")

    # get column names
    #
    column_names = [x.get('name', 'NaN') for x in worldmap_info.attribute_data]

    # get unmatched list (length may not be same as columns--e.g. this is erroneous data)
    #
    unmatched_rows = worldmap_info.core_data.get('unmapped_records_list', [])

    response = HttpResponse(content_type='text/csv')

    file_name = 'unmapped_rows__%s.csv' % (get_datetime_string_for_file())

    response['Content-Disposition'] = 'attachment; filename="%s"' % file_name

    writer = csv.writer(response)
    writer.writerow(column_names)
    for row_info in unmatched_rows:
        writer.writerow(row_info)

    return response


def view_unmatched_lat_lng_rows_json(request, tab_md5):
    """
    View the unmatched rows resulting from trying to map lat/lng columns
    """

    # Retrieve the Tabular file information
    # ----------------------------------
    try:
        worldmap_info = WorldMapLatLngInfo.objects.get(md5=tab_md5)
    except WorldMapLatLngInfo.DoesNotExist:
        raise Http404('No WorldMapLatLngInfo for md5: %s' % tab_md5)

    if worldmap_info.core_data and\
        'unmapped_records_list' in worldmap_info.core_data:
        # Unmatched records exist

        template_dict = dict(ummatched_rows=worldmap_info.core_data['unmapped_records_list'],
                        column_names=worldmap_info.attribute_data)

        unmatched_rows_html = render_to_string('metadata/unmatched_tabular_rows.html',
                                template_dict,
                                request)

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
    # SKIP THIS -> LOOK FOR LAYER IN WORLDMAP EACH TIME
    # Does the file already have an associated WorldMap layer
    # ----------------------------------
    # Getting rid of this -> Fetch new info each time
    #worldmap_tabularinfo = tabular_info.get_worldmap_info()
    #if worldmap_tabularinfo is not None:
    #    # A map exists: show it!
    #    return view_existing_map(request, worldmap_tabularinfo)

    #
    # Is there a WorldMap layer but Geoconnect doesn't know about it?
    #
    if add_worldmap_layerinfo_if_exists(tabular_info):
        # A WorldMap layer already exists!
        if not tabular_info.column_names:
            # Make sure the tabular file has been read and we have
            # data on it (e.g. may be re-mapping now and tabular info is
            # freshly retrieved, columns not yet formatted, etc)
            #
            tab_file_stats = TabFileStats.create_from_tabular_info(tabular_info)
            if tab_file_stats.has_error():
                raise Http404(tab_file_stats.error_message)

        worldmap_tabularinfo = tabular_info.get_worldmap_info()
        if worldmap_tabularinfo:
            return view_existing_map(request, worldmap_tabularinfo)


    # ----------------------------------
    # Open the file and get the stats
    # ----------------------------------
    tab_file_stats = TabFileStats.create_from_tabular_info(tabular_info)
    if tab_file_stats.has_error():
        raise Http404(tab_file_stats.error_message)

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
    #print 'available_layers_list', available_layers_list
    # ----------------------------------
    # Create a Django form for table join column selection
    # ----------------------------------
    #print 'tab_file_stats.column_names', type(tab_file_stats.column_names)

    if available_layers_list and len(available_layers_list) > 0:
        form_single_column = ChooseSingleColumnForm(\
                                    tabular_file_info_id=tabular_info.id,
                                    layer_choices=available_layers_list,
                                    column_names=tab_file_stats.column_names)
    else:
        form_single_column = None

    # ----------------------------------
    # Create a form for Lat/Lng column selection
    # ----------------------------------
    if tab_file_stats:
        form_lat_lng = LatLngColumnsForm(\
                            tabular_file_info_id=tabular_info.id,\
                            column_names=tab_file_stats.column_names)
    else:
        form_lat_lng = None

    template_dict = get_common_lookup(request)

    template_dict.update(dict(\
                    tabular_id=tabular_info.id,
                    tabular_md5=tabular_info.md5,
                    gis_data_info=tabular_info,
                    tab_file_stats=tab_file_stats,
                    geocode_types=geocode_type_list,
                    NUM_PREVIEW_ROWS=num_preview_rows,
                    test_files=TabularFileInfo.objects.all(),
                    form_single_column=form_single_column,
                    form_lat_lng=form_lat_lng,
                    GEO_TYPE_LATITUDE_LONGITUDE=GEO_TYPE_LATITUDE_LONGITUDE,
                    page_title=PANEL_TITLE_MAP_DATA_FILE))

    template_dict[GEOCONNECT_STEP_KEY] = STEP1_EXAMINE
    template_dict['GEOCONNECT_STEPS'] = GEOCONNECT_STEPS

    return render(request, 'tabular_files/main_outline_tab.html', template_dict,)


def ajax_get_all_join_targets_with_descriptions(request):

    return ajax_join_targets_with_descriptions(request, None)


def ajax_join_targets_with_descriptions(request, selected_geo_type=None):
    """For use when choosing a join target through the UI
    Return JSON list with:
       join target id
       name
       description
    """
    jt = get_latest_jointarget_information()

    join_target_info = jt.get_available_layers_list_by_type(selected_geo_type, for_json=True)

    if join_target_info is None:
        err_msg = "Sorry! No Join Targets found for Geospatial type: {0}".format(selected_geo_type)
        json_msg = MessageHelperJSON.get_json_msg(success=False,\
                                msg=err_msg)
        return HttpResponse(status=400, content=json_msg, content_type="application/json")

    else:
        json_msg = MessageHelperJSON.get_json_msg(success=True,\
                                msg="success",\
                                data_dict=join_target_info)

        return HttpResponse(status=200, content=json_msg, content_type="application/json")

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
        err_msg = ("Sorry! No Join Targets found"
                   " for Geospatial type: %s") % selected_geo_type

        json_msg = MessageHelperJSON.get_json_msg(success=False,
                                                  msg=err_msg)
        return HttpResponse(status=400,
                            content=json_msg,
                            content_type="application/json")


    json_msg = MessageHelperJSON.get_json_msg(success=True,
                                              msg="success",
                                              data_dict=join_target_info)

    return HttpResponse(status=200, content=json_msg, content_type="application/json")


"""
import csv

#response = HttpResponse(content_type='text/csv')
#response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'

writer = csv.writer(response)
writer.writerow(['First row', 'Foo', 'Bar', 'Baz'])
writer.writerow(['Second row', 'A', 'B', 'C', '"Testing"', "Here's a quote"])

return response

"""
