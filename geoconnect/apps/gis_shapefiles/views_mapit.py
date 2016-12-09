"""
Views to handle Dataverse initial requests
"""
from django.shortcuts import render_to_response

from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.conf import settings

from geo_utils.msg_util import msg, msgt

from geo_utils.geoconnect_step_names import GEOCONNECT_STEP_KEY, STEP1_EXAMINE
from apps.layer_types.static_vals import is_valid_dv_type,\
                is_dv_type_shapefile,\
                is_dv_type_tabular,\
                is_dv_type_geotiff
from apps.gis_shapefiles.shp_services import get_shapefile_from_dv_api_info
from apps.gis_shapefiles.initial_request_helper import InitialRequestHelper


from apps.gis_tabular.tab_services import get_tabular_file_from_dv_api_info

from apps.registered_dataverse.utils import is_setting_active
from apps.registered_dataverse.views import view_filetype_note_by_name

from geo_utils.view_util import get_common_lookup

import logging
LOGGER = logging.getLogger(__name__)

from geo_utils.template_constants import FAILED_TO_IDENTIFY_METADATA_MAPPING_TYPE


def view_formatted_error_page(request, error_type, err_msg=None):
    """Show an error page"""

    d = get_common_lookup(request)
    d['page_title'] = 'Examine Shapefile'
    d['WORLDMAP_SERVER_URL'] = settings.WORLDMAP_SERVER_URL
    d[GEOCONNECT_STEP_KEY] = STEP1_EXAMINE

    d['Err_Found'] = True
    if error_type is not None:
        d[error_type] = True
    d['Dataverse_Connect_Err_Msg'] = err_msg

    return render_to_response('gis_shapefiles/view_shapefile_overview.html'\
                                , d\
                                , context_instance=RequestContext(request)\
                            )


def view_mapit_incoming_token64(request, dataverse_token):
    """
    (1) Check incoming url for a callback key 'cb'
        and use the callback url to retrieve the DataverseInfo via a POST
    (2) Route the request depending on the type of data returned
    """

    # (1) Check incoming url for a callback url
    # and use the url to retrieve the DataverseInfo via a POST
    #
    request_helper = InitialRequestHelper(request, dataverse_token)
    if request_helper.has_err:
        return view_formatted_error_page(request,\
                            request_helper.err_type,\
                            request_helper.err_msg)


    # (2) Route the request depending on the type of data returned
    #
    mapping_type = request_helper.mapping_type

    #  Is the mapping type valid?
    #  Knowingly redundant, also checked in requestHelper
    #
    if not is_valid_dv_type(mapping_type):

        err_msg = 'The mapping_type for this metadata was not valid.  Found: %s' % mapping_type

        return view_formatted_error_page(request,\
                            FAILED_TO_IDENTIFY_METADATA_MAPPING_TYPE,\
                            err_msg)

    #  Is the mapping type active?
    #
    if not is_setting_active(mapping_type):
        return view_filetype_note_by_name(request, mapping_type)


    # Let's route it!
    #
    if is_dv_type_shapefile(mapping_type):
        return process_shapefile_info(request,\
                            request_helper.dataverse_token,\
                            request_helper.dv_data_dict)

    elif is_dv_type_tabular(mapping_type):

        return process_tabular_file_info(request,\
                            request_helper.dataverse_token,\
                            request_helper.dv_data_dict)

    elif is_dv_type_geotiff(mapping_type):

        err_msg = 'Sorry! GeoTiff mapping is currently not available'
        return view_formatted_error_page(None, err_msg)

    return HttpResponse('Error!!  Should never reach this line!')



def process_tabular_file_info(request, dataverse_token, data_dict):
    """
    Use the shapefile metadata to
        #   (1) Validate the DataverseInfo returned by Dataverse
        #   (2) Create a TabularFileInfo object
        #   (3) Download the dataverse file
    """
    success, tab_md5_or_err_msg = get_tabular_file_from_dv_api_info(dataverse_token, data_dict)

    if not success:
        return view_formatted_error_page(request\
                                         , tab_md5_or_err_msg.err_type\
                                         , tab_md5_or_err_msg.err_msg)

    view_tab_file_first_time_url = reverse('view_tabular_file'\
                                    , kwargs=dict(tab_md5=tab_md5_or_err_msg))

    return HttpResponseRedirect(view_tab_file_first_time_url)


def process_shapefile_info(request, dataverse_token, data_dict):
    """
    Use the shapefile metadata to
        #   (1) Validate the DataverseInfo returned by Dataverse
        #   (2) Create a ShapefileInfo object
        #   (3) Download the dataverse file
    """

    success, shp_md5_or_err_msg = get_shapefile_from_dv_api_info(dataverse_token, data_dict)

    if not success:
        return view_formatted_error_page(request\
                                         , shp_md5_or_err_msg.err_type\
                                         , shp_md5_or_err_msg.err_msg)

    view_shapefile_first_time_url = reverse('view_shapefile_first_time'\
                                    , kwargs=dict(shp_md5=shp_md5_or_err_msg))

    return HttpResponseRedirect(view_shapefile_first_time_url)
