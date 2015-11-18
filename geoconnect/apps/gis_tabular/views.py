from django.shortcuts import render_to_response

from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.conf import settings

from apps.gis_tabular.models import SimpleTabularTest   # for testing

from apps.gis_tabular.tabular_helper import TabFileStats, NUM_PREVIEW_ROWS

from apps.worldmap_connect.utils import get_latest_jointarget_information

from geo_utils.message_helper_json import MessageHelperJSON

#from geo_utils.msg_util import *
#from geo_utils.geoconnect_step_names import GEOCONNECT_STEP_KEY, STEP1_EXAMINE
#from apps.gis_shapefiles.shp_services import get_shapefile_from_dv_api_info
#from geo_utils.view_util import get_common_lookup

import logging
logger = logging.getLogger(__name__)


def view_test_1(request, tabular_id):

    try:
        tabular_info = SimpleTabularTest.objects.get(pk=tabular_id)
    except SimpleTabularTest.DoesNotExist:
        raise Http404('No SimpleTabularTest for id: %s' % tabular_id)

    tab_file_stats = TabFileStats.create_tab_stats_from_tabular_info(tabular_info)

    num_preview_rows = min([x for x in (NUM_PREVIEW_ROWS, tabular_info.num_rows) if x > 0])

    jt = get_latest_jointarget_information()
    geocode_type_list = ['Latitude/Longitude']
    geocode_types_from_worldmap = jt.get_geocode_types()
    if geocode_types_from_worldmap:
        geocode_type_list += geocode_types_from_worldmap

    d = dict(tabular_id=tabular_id,\
            tabular_info=tabular_info,\
            tab_file_stats=tab_file_stats,\
            geocode_types=geocode_type_list,\
            NUM_PREVIEW_ROWS=num_preview_rows)

    return render_to_response('gis_tabular/view_test_1.html', d\
                                     , context_instance=RequestContext(request))


def ajax_get_join_targets(request, selected_geo_type):


    return HttpResponse()
