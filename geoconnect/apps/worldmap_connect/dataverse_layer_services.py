import sys

from dataverse_info.forms import CheckForExistingLayerFormBasic, CheckForDataverseUserLayersFormBasic

from apps.worldmap_connect.worldmap_api_url_helper import GET_LAYER_INFO_BY_USER_AND_FILE_API_PATH, GET_LAYER_INFO_BY_USER_API_PATH

from geo_utils.message_helper_json import MessageHelperJSON

"""
Functions that interact with the WorldMap API to:

    - Retrieve layer information for a specific dv_user_id and dv_file_id
    - Retrieve all layer information for a specific dv_user_id

"""
logger = logging.getLogger(__name__)

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
        
        # Prepare the data
        #
        data_params = f.cleaned_data
        data_params[settings.WORLDMAP_TOKEN_NAME_FOR_DV] = settings.WORLDMAP_TOKEN_FOR_DATAVERSE
         
        # Make the request
        #       
        r = requests.post(GET_LAYER_INFO_BY_USER_AND_FILE_API_PATH\
                        , data=data_params\
                        , timeout=30)
                        
        # Response looks good
        #
        if r.status_code == 200:
            response_dict = r.json()
            return MessageHelperJSON.get_dict_msg(success=True, msg='layer returned', data_dict=data_dict)
            
        # Response doesn't look good
        #
        err_msg = "Status code: %s\nError: %s" % (r.status_code, r.text)
        return MessageHelperJSON.get_dict_msg(success=False, msg=err_msg)
            
    except:
        # Error with request
        #
        err_msg = "Unexpected error: %s" % sys.exc_info()[0]
        return MessageHelperJSON.get_dict_msg(success=False, msg=err_msg)
            
        
    
    