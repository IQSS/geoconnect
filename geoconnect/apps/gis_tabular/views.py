from django.shortcuts import render_to_response

from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.conf import settings

from django.views.decorators.http import require_POST

from apps.gis_tabular.models import SimpleTabularTest   # for testing
from apps.gis_tabular.forms import LatLngColumnsForm, ChooseSingleColumnForm
from apps.gis_tabular.tabular_helper import TabFileStats, NUM_PREVIEW_ROWS

from apps.worldmap_connect.utils import get_latest_jointarget_information

from geo_utils.message_helper_json import MessageHelperJSON
from apps.worldmap_connect.lat_lng_service import create_map_from_datatable_lat_lng
#from geo_utils.msg_util import *
#from geo_utils.geoconnect_step_names import GEOCONNECT_STEP_KEY, STEP1_EXAMINE
#from apps.gis_shapefiles.shp_services import get_shapefile_from_dv_api_info
#from geo_utils.view_util import get_common_lookup

import logging
logger = logging.getLogger(__name__)


@require_POST
def view_map_tabular_file_form(request):
    """
    Join your tabular file to a WorldMap layer
    using the column selected in this form
    """
    for k, v in request.POST.items():
        print k, v

    json_msg = MessageHelperJSON.get_json_success_msg('You got here! (view_map_tabular_file_form)')
    return HttpResponse(json_msg, mimetype="application/json", status=200)




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

        json_msg = MessageHelperJSON.get_json_fail_msg(f.err_msg_for_web)
        return HttpResponse(json_msg, mimetype="application/json", status=200)

        #print f.errors.items()
        #print 'Type: ', type(f)
        #print dir(f)#'Type: ', type(f)
        #print 'f.is_valid(): %s' % f.is_valid()


    (success, worldmap_msg) = create_map_from_datatable_lat_lng(tabular_info,
                        f.get_latitude_colname(),
                        f.get_longitude_colname(),
                        )

    if success:
        json_msg = MessageHelperJSON.get_json_success_msg(worldmap_msg)
    else:
        json_msg = MessageHelperJSON.get_json_fail_msg('Sorry! ' + worldmap_msg)

    return HttpResponse(json_msg, mimetype="application/json", status=200)


def view_test_file(request, tabular_id):


    try:
        tabular_info = SimpleTabularTest.objects.get(pk=tabular_id)
    except SimpleTabularTest.DoesNotExist:
        raise Http404('No SimpleTabularTest for id: %s' % tabular_id)

    tab_file_stats = TabFileStats.create_tab_stats_from_tabular_info(tabular_info)

    num_preview_rows = min([x for x in (NUM_PREVIEW_ROWS, tabular_info.num_rows) if x > 0])

    join_target_info = get_latest_jointarget_information()
    geocode_type_list = [( u'latitude-longitude', u'Latitude/Longitude')]
    geocode_types_from_worldmap = join_target_info.get_geocode_types()
    if geocode_types_from_worldmap:
        geocode_type_list += geocode_types_from_worldmap

    available_layers_list = join_target_info.get_available_layers_list()

    # Create a form for table join column selection
    #
    if available_layers_list and len(available_layers_list) > 0:
        form_single_column = ChooseSingleColumnForm(tabular_file_info_id=tabular_info.id,
                    layer_choices=available_layers_list,
                    column_names=tab_file_stats.column_names)
    else:
        form_lat_lng = None
        form_single_column = None

    # Create a form for Lat/Lng column selection
    #
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
            form_lat_lng=form_lat_lng)

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

    join_target_info = jt.get_join_targets_by_type(selected_geo_type)
    if join_target_info is None:
        err_msg = "Sorry! No Join Targets found for Geospatial type: {0}".format(selected_geo_type)
        json_msg = MessageHelperJSON.get_json_msg(success=False,\
                                msg=err_msg)
        return HttpResponse(status=400, content=json_msg, content_type="application/json")


    json_msg = MessageHelperJSON.get_json_msg(success=True,\
                                msg="success",\
                                data_dict=join_target_info)

    return HttpResponse(status=200, content=json_msg, content_type="application/json")
