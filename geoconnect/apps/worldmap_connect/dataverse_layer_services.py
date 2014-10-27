from dataverse_info.forms import CheckForExistingLayerFormBasic, CheckForDataverseUserLayersFormBasic

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
        
        data_params = f.cleaned_data
        data_params[settings.WORLDMAP_TOKEN_NAME_FOR_DV] = settings.WORLDMAP_TOKEN_FOR_DV
        
        worldmap_url = settings.WORLDMAP_SERVER_URL  + '/dvn-layer/get-existing-layer-info/'
        
        r = requests.post(worldmap_url\
                        , data=data_params\
                        , timeout=30)
    except:
        return None
    """  
        if request.status
        wm_response_dict = r.json()
        logger.debug('response: %s' % wm_response_dict)
        if wm_response_dict.get('success', False) is True and wm_response_dict.get('data') is not None:
            wm_response_dict.pop('success')
            return self.get_result_msg(True, '', data_dict=wm_response_dict.get('data'))
                            
        elif wm_response_dict.has_key('message'):
            err_msgs = wm_response_dict['message']
            return self.get_result_msg(False, err_msgs)
    """
    return None
    
    