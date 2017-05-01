"""
Calls to the WorldMap API to:
    - Delete a dataverse created map layer
        - params: DV installation name, DV file id
    - Get layer information
        - params: DV installation name, DV file id
    - Retrieve available join targets

"""
from __future__ import print_function

import sys
import logging
import requests

from django.conf import settings

from gc_apps.gis_basic_file.models import GISDataFile

from gc_apps.gis_basic_file.dataverse_info_service import get_dataverse_info_dict

from shared_dataverse_information.dataverse_info.forms_existing_layer import\
        CheckForExistingLayerForm
from shared_dataverse_information.worldmap_api_helper.url_helper import\
        GET_LAYER_INFO_BY_DATAVERSE_INSTALLATION_AND_FILE_API_PATH,\
        DELETE_LAYER_API_PATH,\
        GET_JOIN_TARGETS,\
        DELETE_TABLEJOIN

from gc_apps.geo_utils.message_helper_json import MessageHelperJSON

"""
Functions that interact with the WorldMap API to:

    - Retrieve layer information for a specific dv_user_id and dv_file_id
    - Retrieve all layer information for a specific dv_user_id

"""
LOGGER = logging.getLogger(__name__)


def delete_map_layer(gis_data_info, worldmap_layer_info):
    """
    Delete a Layer from the WorldMap, using the WorldMap API

    returns (True, None)
        or (False, 'error message of some type')
    """
    assert isinstance(gis_data_info, GISDataFile), "gis_data_file must be a GISDataFile object"
    #assert isinstance(worldmap_layer_info, WorldMapLayerInfo),\
    #        "worldmap_layer_info must be a WorldMapLayerInfo object"

    #--------------------------------------
    # Does the GISDataFile object correspond
    #    to the WorldMapLayerInfo object?
    #--------------------------------------
    if worldmap_layer_info.get_gis_data_info() != gis_data_info:
        err_msg = ('Error the GISDataFile does not correspond'
                   ' to the WorldMapLayerInfo object.')
        LOGGER.error(err_msg)
        return (False, err_msg)

    #   For join layers, remove the TableJoin object
    #
    if worldmap_layer_info.is_join_layer():
        return delete_worldmap_tablejoin(worldmap_layer_info)


    #--------------------------------------
    # Prepare params for WorldMAP API call
    #--------------------------------------
    data_params = get_dataverse_info_dict(gis_data_info)
    existing_layer_form = CheckForExistingLayerForm(data_params)
    if not existing_layer_form.is_valid():
        err_msg = """Error.  Validation failed. (CheckForExistingLayerForm)"""
        LOGGER.error(err_msg)
        return (False, err_msg)

    #
    data_params = existing_layer_form.cleaned_data

    print ('DELETE_LAYER_API_PATH: %s' % DELETE_LAYER_API_PATH)
    print ("data_params: %s" % data_params)
    try:
        r = requests.post(DELETE_LAYER_API_PATH\
                        , data=data_params\
                        , auth=settings.WORLDMAP_ACCOUNT_AUTH\
                        , timeout=settings.WORLDMAP_SHORT_TIMEOUT)
    except requests.exceptions.ConnectionError as exception_obj:

        err_msg = ('Failed to retrieve data from the WorldMap.'
                   '<p><b>Details for administrator:</b>'
                   ' Could not contact the WorldMap'
                   ' server: {0}</p>').format(DELETE_LAYER_API_PATH)

        LOGGER.error(err_msg + '\nConnectionError:' + exception_obj.message)

        return (False, err_msg)

    print (r.text)
    print (r.status_code)

    #--------------------------------------
    # Check Response
    #--------------------------------------
    if r.status_code == 200:
        #response_dict = r.json()
        return (True, None)

    #--------------------------------------
    # Response doesn't look good
    #--------------------------------------
    err_msg = "Status code: %s\nError: %s" % (r.status_code, r.text)
    LOGGER.error(err_msg)

    return (False, err_msg)


def delete_worldmap_tablejoin(worldmap_layer_info):
    """
    Use the WorldMap API to delete a TableJoin object
    """
    if not (hasattr(worldmap_layer_info, 'is_join_layer') and\
        worldmap_layer_info.is_join_layer()):
        return (False, 'Expected a WorldMapJoinLayerInfo object')

    if not worldmap_layer_info.core_data:
        return (False, 'Could not find core join layer data')

    tablejoin_id = worldmap_layer_info.core_data.get('tablejoin_id', None)
    if tablejoin_id is None:
        return (False, 'Failed to find the TableJoin id.')

    delete_api_path = '%s%s' % (DELETE_TABLEJOIN, tablejoin_id)
    print ('delete_api_path: %s' % delete_api_path)

    try:
        resp = requests.post(delete_api_path,
                             auth=settings.WORLDMAP_ACCOUNT_AUTH,
                             timeout=settings.WORLDMAP_SHORT_TIMEOUT)

    except requests.exceptions.ConnectionError as exception_obj:

        err_msg = ('Failed to delete the map.'
                   '<p><b>Details for administrator:</b>'
                   'Could not contact the WorldMap server: %s</p>') %\
                    (delete_api_path)

        LOGGER.error('ConnectionError during delete: %s', exception_obj.message)
        LOGGER.error('delete_api_path: %s', delete_api_path)
        return (False, err_msg)

    print (resp.text)
    print (resp.status_code)

    #--------------------------------------
    # Check Response
    #--------------------------------------
    if resp.status_code == 200:
        #response_dict = r.json()
        return (True, None)
    elif resp.status_code == 404:
        # TableJoin no longer exists
        return (True, None)

    #--------------------------------------
    # Response doesn't look good
    #--------------------------------------
    err_msg = "Status code: %s\nError: %s" % (resp.status_code, resp.text)
    LOGGER.error(err_msg)

    return (False, err_msg)



"""
url = 'http://127.0.0.1:8000/dvn-layer/get-dataverse-user-layers/'
url = 'http://127.0.0.1:8000/dvn-layer/get-existing-layer-info/'
"""
def get_layer_info_using_dv_info(params_dict):
    """
    Retrieve WorldMap layer information via API

    params_dict needs to include:
        - dataverse_installation_name
        - datafile_id

    Fail: (False, error message)
    Success: (True, python dict)
    """
    f = CheckForExistingLayerForm(params_dict)
    if not f.is_valid():
        err_msg = """Sorry! Failed to validate the request to retrieve WorldMap layer metadata."""
        LOGGER.error(err_msg + \
        "  Validation failure for CheckForExistingLayerForm.  Errors: %s" % f.errors)
        return False, err_msg


    #--------------------------------------
    # Prepare the data
    #--------------------------------------
    data_params = f.cleaned_data

    #--------------------------------------
    # Make the request
    #--------------------------------------
    try:
        resp = requests.post(GET_LAYER_INFO_BY_DATAVERSE_INSTALLATION_AND_FILE_API_PATH\
                        , data=data_params\
                        , auth=settings.WORLDMAP_ACCOUNT_AUTH\
                        , timeout=settings.WORLDMAP_SHORT_TIMEOUT)
    except requests.exceptions.ConnectionError as exception_obj:

        err_msg = """Sorry! Failed to retrieve data from the WorldMap.
                    <p><b>Details for administrator:</b> Could not contact the
                    WorldMap server: %s</p>"""\
                    % (GET_LAYER_INFO_BY_DATAVERSE_INSTALLATION_AND_FILE_API_PATH)
        LOGGER.error(err_msg)
        LOGGER.error('ConnectionError: %s', exception_obj)
        return False, err_msg
    except:
        # Error with request
        #
        err_msg = "Unexpected error: %s" % sys.exc_info()[0]
        LOGGER.error(err_msg)
        return False, err_msg

    print (resp.text)
    print (resp.status_code)

    #--------------------------------------
    # Response looks good
    #--------------------------------------
    if resp.status_code == 200:
        try:
            response_dict = resp.json()
        except ValueError:
            err_msg = "Failed to convert response to JSON."
            LOGGER.error(err_msg + "Status code: 200.\nResponse text: %s" % resp.text)
            return False, err_msg

        return response_dict.get('success', False), response_dict

    #--------------------------------------
    # Response doesn't look good
    #--------------------------------------
    err_msg = "Status code: %s\nError: %s" % (resp.status_code, resp.text)
    return False, err_msg


def get_join_targets_as_json():
    """
    Retrieve JoinTarget information from WorldMap and
    return it in JSON format
    """

    (success, data_dict_or_error_msg) = get_join_targets()
    if success is True:
        return MessageHelperJSON.get_dict_msg(success=True,\
                    msg="Join Targets retrieved",\
                    data_dict=data_dict_or_error_msg)

    else:
        return MessageHelperJSON.get_dict_msg(success=False,\
                    msg=data_dict_or_error_msg)



def get_join_targets():
    """
    Using the WorldMap API, retrieve a list of available tabular file JointTargets

        ...datatables/api/jointargets/
    """
    #--------------------------------------
    # Make the request
    #--------------------------------------
    try:
        r = requests.get(GET_JOIN_TARGETS\
                        , auth=settings.WORLDMAP_ACCOUNT_AUTH\
                        , timeout=settings.WORLDMAP_SHORT_TIMEOUT)
    except requests.exceptions.ConnectionError as exception_obj:

        err_msg = ('Sorry! Failed to retrieve data from the WorldMap.'
                   '<p><b>Details for administrator:</b>'
                   ' Could not contact the'
                   ' WorldMap server: %s</p>(err-id: 1))') %\
                   (GET_JOIN_TARGETS)

        LOGGER.error(err_msg)
        LOGGER.error('ConnectionError: %s', exception_obj.message)
        return (False, err_msg)

    except:
        # Error with request
        #
        err_msg = ('Sorry! Failed to retrieve data from the WorldMap.'
                   '<p><b>Details for administrator:</b>'
                   ' Could not contact the'
                   ' WorldMap server: %s</p>(err-id: 2))') %\
                   (GET_JOIN_TARGETS)
        LOGGER.error(err_msg)
        LOGGER.error(sys.exc_info()[0])

        return (False, err_msg)

    #--------------------------------------
    # Convert to JSON
    #--------------------------------------
    try:
        response_dict = r.json()
    except:
        err_msg = "Failed to convert response to JSON."
        LOGGER.error(err_msg + "Status code: %s.\nResponse text: %s",\
            r.status_code, r.text)
        return (False, err_msg)


    #--------------------------------------
    # Response looks good
    #--------------------------------------
    if r.status_code == 200 and\
        'data' in response_dict:
        return (True, response_dict)

    #--------------------------------------
    # Response doesn't look good
    #--------------------------------------
    default_err_msg = 'Join target retrieval failed. Status code\
        {0}. Response text: {1}'.format(r.status_code,
                                        r.text)
    err_msg = response_dict.get('message', default_err_msg)
    LOGGER.error(err_msg)
    return (False, err_msg)



"""
# Test, join target retreval from WorldMap
# ---------------------
python manage.py shell
from gc_apps.worldmap_connect.dataverse_layer_services import *
get_join_targets()

"""
"""
python manage.py shell

from gc_apps.worldmap_connect.dataverse_layer_services import *


"""
