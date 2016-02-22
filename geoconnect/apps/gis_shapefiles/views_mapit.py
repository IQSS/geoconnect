import json
import requests

from django.shortcuts import render_to_response

from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.conf import settings

from geo_utils.msg_util import *

from geo_utils.geoconnect_step_names import GEOCONNECT_STEP_KEY, STEP1_EXAMINE

from apps.gis_shapefiles.shp_services import get_shapefile_from_dv_api_info
from apps.gis_tabular.tab_services import get_tabular_file_from_dv_api_info

from geo_utils.view_util import get_common_lookup

import logging
logger = logging.getLogger(__name__)

FAILED_TO_RETRIEVE_DATAVERSE_FILE = 'FAILED_TO_RETRIEVE_DATAVERSE_FILE'
FAILED_TO_CONVERT_RESPONSE_TO_JSON = 'FAILED_TO_CONVERT_RESPONSE_TO_JSON'
FAILED_BAD_STATUS_CODE_FROM_WORLDMAP = 'FAILED_BAD_STATUS_CODE_FROM_WORLDMAP'
FAILED_TO_IDENTIFY_METADATA_MAPPING_TYPE = 'FAILED_TO_IDENTIFY_METADATA_MAPPING_TYPE'

def view_formatted_error_page(request, error_type, err_msg=None):

    d = get_common_lookup(request)
    d['page_title'] = 'Examine Shapefile'
    d['WORLDMAP_SERVER_URL'] = settings.WORLDMAP_SERVER_URL
    d[GEOCONNECT_STEP_KEY] = STEP1_EXAMINE

    d['Err_Found'] = True
    if error_type is not None:
        d[error_type] = True
    d['Dataverse_Connect_Err_Msg'] = err_msg

    return render_to_response('gis_shapefiles/view_02_single_shapefile.html'\
                                , d\
                                , context_instance=RequestContext(request)\
                            )


def view_mapit_incoming_token64(request, dataverse_token):
    """
    This needs to be re-factored

    (1) Check incoming url for a callback key 'cb'
    (2) Use the callback url to retrieve the DataverseInfo via a POST
    """
    assert request.GET is not None, "request.GET cannot be None"
    assert request.GET.has_key('cb') is True, "request.GET must have key 'cb' for the callback url"

    callback_url = request.GET['cb']# + "?%s" % urlencode(dict(key='pete'))

    # hack for testing until dvn-build is updated
    #
    if callback_url.find('dvn-build') > -1 and callback_url.find('https') == -1:
        callback_url = callback_url.replace('http', 'https')

    # Make a post request using the temporary token issued by WorldMap
    #
    TOKEN_PARAM = {settings.DATAVERSE_TOKEN_KEYNAME : dataverse_token}

    """
    #http://127.0.0.1:8070/shapefile/map-it/fe1b5f64adcbf2c2c4742fe5eaa0dd6887f410d02317361d9c999c2d4cdaa63e/?cb=http%3A%2F%2Flocalhost%3A8010%2Fapi%2Fworldmap%2Fdatafile%2F
    """
    try:
        r = requests.post(callback_url, data=json.dumps(TOKEN_PARAM))
    except requests.exceptions.ConnectionError as e:

        err_msg = '<p><b>Details for administrator:</b> Could not contact the Dataverse server: %s</p><p>%s</p>'\
                                % (callback_url, e.message)
        logger.error(err_msg)
        return view_formatted_error_page(request\
                                        , FAILED_TO_RETRIEVE_DATAVERSE_FILE\
                                        , err_msg)

    #msgt(r.text)
    #msg(r.status_code)

    # ------------------------------
    # Check if valid status code
    # ------------------------------
    if not r.status_code == 200:
        err_msg1 = 'Status code from dataverse: %s' % (r.status_code)
        err_msg2 = err_msg1 + '\nResponse: %s' % (r.text)
        logger.error(err_msg2)
        return view_formatted_error_page(request\
                                        , FAILED_TO_RETRIEVE_DATAVERSE_FILE\
                                        , err_msg1)

        #return HttpResponse("Sorry! Failed to retrieve Dataverse file")

    # ------------------------------
    # Attempt to convert response to JSON
    # ------------------------------
    jresp = r.json()
    if not type(jresp) is dict:
        err_msg1 = 'Failed to convert response to JSON\nStatus code from dataverse: %s' % (r.status_code)
        err_msg2 = err_msg1 + '\nResponse: %s' % (r.text)
        logger.error(err_msg2)
        return view_formatted_error_page(request\
                                         , FAILED_TO_CONVERT_RESPONSE_TO_JSON\
                                         , err_msg1)


    # ------------------------------
    # Examine response
    #
    # (1) Identify the mapping type
    # (2) Send the file through the appropriate path
    #   - e.g. shapefile, tabular file, etc.
    # ------------------------------
    if jresp.has_key('status') and jresp['status'] in ['OK', 'success']:

        data_dict = jresp.get('data')
        mapping_type = data_dict.pop('mapping_type', None)

        if mapping_type == 'shapefile':
            return process_shapefile_info(request, dataverse_token, data_dict)
        elif mapping_type == 'tabular':
            return process_tabular_file_info(request, dataverse_token, data_dict)
        else:
            err_msg = 'The mapping_type for this metadata was not found.  Found: %s' % mapping_type
            err_msg2 = err_msg1 + '\nResponse: %s' % (r.text)
            logger.error(err_msg2)
            return view_formatted_error_page(request\
                                     , FAILED_TO_IDENTIFY_METADATA_MAPPING_TYPE\
                                     , err_msg1)

    # ------------------------------
    # Failed!
    # ------------------------------
    err_msg1 = 'Unsuccessful request to Dataverse\nStatus code from dataverse: %s\nStatus: %s' % (r.status_code, jresp.get('status', 'not found'))
    err_msg2 = err_msg1 + '\nResponse: %s' % (r.text)
    logger.error(err_msg2)
    return view_formatted_error_page(request\
                                     , FAILED_BAD_STATUS_CODE_FROM_WORLDMAP\
                                     , err_msg1)


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

    view_tab_file_first_time_url =  reverse('view_tabular_file'\
                                    , kwargs={ 'tab_md5' : tab_md5_or_err_msg })

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

    view_shapefile_first_time_url =  reverse('view_shapefile_first_time'\
                                    , kwargs={ 'shp_md5' : shp_md5_or_err_msg })

    return HttpResponseRedirect(view_shapefile_first_time_url)
