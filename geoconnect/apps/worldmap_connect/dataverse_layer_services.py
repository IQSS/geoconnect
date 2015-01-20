from __future__ import print_function

import sys
import logging
import requests

from django.conf import settings


from apps.gis_basic_file.models import GISDataFile
from apps.worldmap_connect.models import WorldMapLayerInfo

from shared_dataverse_information.dataverse_info.forms import CheckForExistingLayerFormBasic, CheckForDataverseUserLayersFormBasic
from apps.gis_basic_file.dataverse_info_service import get_dataverse_info_dict

from shared_dataverse_information.worldmap_api_helper.url_helper import GET_LAYER_INFO_BY_USER_AND_FILE_API_PATH\
                                                        , GET_LAYER_INFO_BY_USER_API_PATH\
                                                        , DELETE_LAYER_API_PATH

from geo_utils.message_helper_json import MessageHelperJSON

"""
Functions that interact with the WorldMap API to:

    - Retrieve layer information for a specific dv_user_id and dv_file_id
    - Retrieve all layer information for a specific dv_user_id

"""
logger = logging.getLogger(__name__)


def delete_map_layer(gis_data_file, worldmap_layer_info):
    """
    Delete a Layer from the WorldMap, using the WorldMap API
    
    returns (True, None)
        or (False, 'error message of some type')
    """
    assert isinstance(gis_data_file, GISDataFile), "gis_data_file must be a GISDataFile object"
    assert isinstance(worldmap_layer_info, WorldMapLayerInfo), "worldmap_layer_info must be a WorldMapLayerInfo object"
    
    #--------------------------------------
    # Does the GISDataFile object correspond 
    #    to the WorldMapLayerInfo object?
    #--------------------------------------
    if worldmap_layer_info.import_attempt and worldmap_layer_info.import_attempt.gis_data_file:
        if not gis_data_file == worldmap_layer_info.import_attempt.gis_data_file:
            err_msg = """Error the GISDataFile does not correspond to the WorldMapLayerInfo object."""
            logger.error(err_msg)
            return (False, err_msg)


    #--------------------------------------
    # Prepare params for WorldMAP API call
    #--------------------------------------
    data_params = get_dataverse_info_dict(gis_data_file)
    data_params[settings.WORLDMAP_TOKEN_NAME_FOR_DV] = settings.WORLDMAP_TOKEN_FOR_DATAVERSE
    print ('DELETE_LAYER_API_PATH: %s' % DELETE_LAYER_API_PATH)
    print ("data_params: %s" % data_params)
    try:
         r = requests.post(DELETE_LAYER_API_PATH\
                        , data=data_params\
                        , timeout=30)
    except requests.exceptions.ConnectionError as e:

        err_msg = """Sorry! Failed to retrieve data from the WorldMap.
                    <p><b>Details for administrator:</b> Could not contact the
                    WorldMap server: %s</p><p>%s</p>"""\
                                % (DELETE_LAYER_API_PATH, e.message)
        logger.error(err_msg)
        return (False, err_msg)

    print (r.text)
    print (r.status_code)

    #--------------------------------------
    # Check Response
    #--------------------------------------
    if r.status_code == 200:
        
        response_dict = r.json()
        return (True, None)
    
    #--------------------------------------
    # Response doesn't look good
    #--------------------------------------
    err_msg = "Status code: %s\nError: %s" % (r.status_code, r.text)
    logger.error(err_msg)
    
    return (False, err_msg)
    
    


"""
url = 'http://127.0.0.1:8000/dvn-layer/get-dataverse-user-layers/'
url = 'http://127.0.0.1:8000/dvn-layer/get-existing-layer-info/'
"""
def get_dataverse_layer_info_by_user_and_file(dv_user_id, datafile_id):
    """
    Retrieve layer information or None
    """
    assert type(dv_user_id) is int, "dv_user_id must be an integer"
    assert type(datafile_id) is int, "dv_file_id must be an integer"
    
    data = dict(dv_user_id=dv_user_id, datafile_id=datafile_id)
    f = CheckForExistingLayerFormBasic(**data)
    if not f.is_valid():
        return None
    
    try:
        logger.debug('get_dataverse_layer_info_by_user_and_file')
        
        #--------------------------------------
        # Prepare the data
        #--------------------------------------
        data_params = f.cleaned_data
        data_params[settings.WORLDMAP_TOKEN_NAME_FOR_DV] = settings.WORLDMAP_TOKEN_FOR_DATAVERSE
         
        #--------------------------------------
        # Make the request
        #--------------------------------------
        try:
            r = requests.post(GET_LAYER_INFO_BY_USER_AND_FILE_API_PATH\
                            , data=data_params\
                            , timeout=30)
        except requests.exceptions.ConnectionError as e:

            err_msg = """Sorry! Failed to retrieve data from the WorldMap.
                        <p><b>Details for administrator:</b> Could not contact the
                        WorldMap server: %s</p><p>%s</p>"""\
                                    % (GET_LAYER_INFO_BY_USER_AND_FILE_API_PATH, e.message)
            logger.error(err_msg)
            return MessageHelperJSON.get_dict_msg(success=False, msg=err_msg)

        #r = requests.post(GET_LAYER_INFO_BY_USER_AND_FILE_API_PATH\
        #                , data=data_params\
        #                , timeout=30)
                        
        #--------------------------------------
        # Response looks good
        #--------------------------------------
        if r.status_code == 200:
            response_dict = r.json()
            return MessageHelperJSON.get_dict_msg(success=True, msg='layer returned', data_dict=data_dict)
            
        #--------------------------------------
        # Response doesn't look good
        #--------------------------------------
        err_msg = "Status code: %s\nError: %s" % (r.status_code, r.text)
        return MessageHelperJSON.get_dict_msg(success=False, msg=err_msg)
            
    except:
        # Error with request
        #
        err_msg = "Unexpected error: %s" % sys.exc_info()[0]
        return MessageHelperJSON.get_dict_msg(success=False, msg=err_msg)
            
        
"""
python manage.py shell

from apps.worldmap_connect.dataverse_layer_services import delete_map_layer
from apps.gis_basic_file.models import GISDataFile
from apps.worldmap_connect.models import WorldMapLayerInfo

gis_data_file = GISDataFile.objects.get(pk=3)
worldmap_layer_info = WorldMapLayerInfo.objects.get(pk=1)

delete_map_layer(gis_data_file, worldmap_layer_info)

"""    
    