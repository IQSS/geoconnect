from __future__ import print_function

import os
import json
import requests # for POST

if __name__=='__main__':
    import sys
    CURRENT_DIR = os.path.dirname(os.path.dirname(__file__))
    sys.path.append(os.path.join(CURRENT_DIR, '../'))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geoconnect.settings.local")

from geo_utils.key_checker import KeyChecker 
from geo_utils.json_field_reader import MessageHelperJSON

from django.conf import settings 
from apps.dv_notify.models import DATAVERSE_REQUIRED_KEYS
import logging
logger = logging.getLogger(__name__)


class MetadataUpdater:
    """Send a metadata update to Dataverse.  Specifically, update the GIS Metadata block
    for a given file."""
    
    #METADATA_UPDATE_API_PATH = 'geo-api/singlefile/update-gis-metadata/'
    REQUIRED_PARAM_KEYS = DATAVERSE_REQUIRED_KEYS
    # ['datafile_id', 'layer_name', 'layer_link', 'embed_map_link', 'worldmap_username', 'dv_session_token']#, 'bbox_min_lng', 'bbox_min_lat', 'bbox_max_lng', 'bbox_max_lat']
    
    def __init__(self, dataverse_server_url, timeout_seconds=240, return_type_json=False):
        """
        Use data in a python dict to POST data to the Dataverse API, specifically the GeographicMetadataUpdateForm
        
        :param dv_metadata_params: dict containing information necessary for contacting dataverse
        """
        self.api_update_url = dataverse_server_url + settings.DATAVERSE_METADATA_UPDATE_API_PATH
        self.timeout_seconds = timeout_seconds
        self.return_type_json = return_type_json
    
    def get_result_msg(self, success=False, msg='', data_dict=None):

        if type(data_dict) is dict:
            print ('YES')
            d = MessageHelperJSON.get_dict_msg(success=success, msg=msg, data_dict=data_dict)
        else:        
            d = MessageHelperJSON.get_dict_msg(success=success, msg=msg)
        
        if not self.return_type_json:
            return d
        
        return MessageHelperJSON.get_json_msg_from_dict(d) 
    
    
    def send_info_to_dataverse(self, dv_metadata_params):
        """
        Go through the process of sending params to dataverse
        :param dv_metadata_params: python dict used to POST to dataverse
        :returns: JSON with "success" flag and either error or data
        :rtype: JSON string
        """
        logger.info('send_params_to_dataverse')
        print('1) send_params_to_dataverse')
        print (dv_metadata_params)
        key_check_response = KeyChecker.has_required_keys(self.REQUIRED_PARAM_KEYS, dv_metadata_params)        
        if not key_check_response.success:
            logger.error(key_check_response.err_msg + ' Info not in "layer_params"')
            return self.get_result_msg(False, key_check_response.err_msg)
            
        print('2) passed key check')
        try:
            print ('params to send: %s' % dv_metadata_params)
            req = requests.post(self.api_update_url, data=json.dumps(dv_metadata_params), timeout=self.timeout_seconds)
            print('3) req: %s' % req)
            
            if not req.status_code == 200:
                logger.error('Metadata update failed.  Status code: %s\nResponse:%s' % (req.status_code, req.text))
                
                return self.get_result_msg(False, 'Sorry! The update failed.')
   
            print (req.text)
            #open('err.html', 'w').write(req.text)

            dv_response_dict = req.json()
            print('4) req to json')
            
            print( dv_response_dict)
            if dv_response_dict.get('status', False) in ('OK', 'success'):
                dv_response_dict.pop('status')
                print('4) send result')
                return self.get_result_msg(True, '', data_dict=dv_response_dict)
                                
            elif dv_response_dict.has_key('message'):
                return self.get_result_msg(False, dv_response_dict['message'])
            return self.get_result_msg(False, 'The update failed.')
                
                
        except requests.exceptions.Timeout:
            return self.get_result_msg(False, 'This request timed out.  (Time limit: %s seconds(s))' % self.timeout_seconds)
        #except:
        #    return self.get_result_msg(False, 'Sorry! The request failed')
            
            
        return self.get_result_msg(False, 'The import failed for an unknown reason')
       
    @staticmethod
    def update_dataverse_with_metadata(worldmap_import_success_obj):
        if worldmap_import_success_obj is None:
            logger.error('worldmap_import_success_obj is None')
            return False
            
        params_for_dv = worldmap_import_success_obj.get_params_for_dv_update()
        mu = MetadataUpdater(settings.DATAVERSE_SERVER_URL)
        resp_dict = mu.send_info_to_dataverse(params_for_dv)
        print ('>>>>>>>>>',resp_dict)
        if resp_dict.get('success', False) is True:
            return True
        return False
    
if __name__ == '__main__':
    #f2 = '../../scripts/worldmap_api/test_shps/poverty_1990_gfz.zip'
    from apps.worldmap_import.models import WorldMapImportSuccess
    
    if WorldMapImportSuccess.objects.count() > 0:
        success_obj = WorldMapImportSuccess.objects.all().order_by('-modified')[0]
        params = success_obj.get_params_for_dv_update()
        print('params to send: %s' % params)

        mu = MetadataUpdater(settings.DATAVERSE_SERVER_URL)
        print (mu.send_info_to_dataverse(params))
    else:
        print('No WorldMapImportSuccess objects')
    
    
    
    
    
    
    
    
       