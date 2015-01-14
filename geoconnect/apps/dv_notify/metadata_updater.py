from __future__ import print_function

import os
import json
import requests # for POST

if __name__=='__main__':
    import sys
    CURRENT_DIR = os.path.dirname(os.path.dirname(__file__))
    sys.path.append(os.path.join(CURRENT_DIR, '../'))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geoconnect.settings.local")

#from geo_utils.key_checker import KeyChecker
from geo_utils.message_helper_json import MessageHelperJSON

from django import forms
from django.conf import settings
from apps.worldmap_connect.models import WorldMapLayerInfo

import logging
logger = logging.getLogger('geoconnect')


class MetadataUpdater:
    """
    Send a metadata update to Dataverse.  Specifically, update the GIS Metadata block
    for a given file.
    """

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
    
    
    def send_info_to_dataverse(self, worldmap_layer_info):
        """
        Go through the process of sending params to dataverse
        :param dv_metadata_params: python dict used to POST to dataverse
        :returns: JSON with "success" flag and either error or data
        :rtype: JSON string
        """
        assert type(worldmap_layer_info) is WorldMapLayerInfo, "worldmap_layer_info must be a WorldMapLayerInfo object"

        logger.info('send_params_to_dataverse')
        print('1) send_params_to_dataverse')

        dv_metadata_params = worldmap_layer_info.get_params_for_dv_update()

        print ('params to send: %s' % dv_metadata_params)
        print ('-' * 40)
        print ('update url: %s' % self.api_update_url)
        print ('-' * 40)
        print ('payload: %s' % json.dumps(dv_metadata_params))
        print ('-' * 40)


        req = None
        try:
            req = requests.post(self.api_update_url, data=json.dumps(dv_metadata_params), timeout=self.timeout_seconds)
        except requests.exceptions.Timeout:
            return self.get_result_msg(False, 'This request timed out.  (Time limit: %s seconds(s))' % self.timeout_seconds)

        except requests.exceptions.ConnectionError as e:

            err_msg = '<p><b>Details for administrator:</b> Could not contact the Dataverse server: %s</p><p>%s</p>'\
                                % (self.api_update_url, e.message)
            logger.error(err_msg)
            return self.get_result_msg(False, err_msg)

        if not req.status_code == 200:
                
            print ('request text: %s' % req.text)
                
            logger.error('Metadata update failed.  Status code: %s\nResponse:%s' % (req.status_code, req.text))
                
            return self.get_result_msg(False, 'Sorry! The update failed.')
   
        print (req.text)
        dv_response_dict = req.json()
        print('4) req to json')
            
        print( dv_response_dict)
        if dv_response_dict.get('status', False) in ('OK', 'success'):
            dv_response_dict.pop('status')
            print('4) send result')
            return self.get_result_msg(True, '', data_dict=dv_response_dict)
                                
        elif dv_response_dict.has_key('message'):
            return self.get_result_msg(False, dv_response_dict['message'])
        else:
            return self.get_result_msg(False, 'The import failed for an unknown reason')

        #    return self.get_result_msg(False, 'The update failed.')
                

        #except:
        #    return self.get_result_msg(False, 'Sorry! The request failed')
            
            

    @staticmethod
    def update_dataverse_with_metadata(worldmap_layer_info):
        assert isinstance(worldmap_layer_info, WorldMapLayerInfo), '"worldmap_layer_info" must be a WorldMapLayerInfo object.'
    
        #params_for_dv = worldmap_layer_info.get_params_for_dv_update()
        mu = MetadataUpdater(settings.DATAVERSE_SERVER_URL)
        resp_dict = mu.send_info_to_dataverse(worldmap_layer_info)
        print ('>>>>>>>>>',resp_dict)
        if resp_dict.get('success', False) is True:
            return True
        return False

    
if __name__ == '__main__':
    #f2 = '../../scripts/worldmap_api/test_shps/poverty_1990_gfz.zip'
    from apps.worldmap_connect.models import WorldMapLayerInfo
    
    if WorldMapLayerInfo.objects.count() > 0:
        success_obj = WorldMapLayerInfo.objects.all().order_by('-modified')[0]
        #params = success_obj.get_params_for_dv_update()
        #print('params to send: %s' % params)

        mu = MetadataUpdater(settings.DATAVERSE_SERVER_URL)
        print (mu.send_info_to_dataverse(success_obj))
    else:
        print('No WorldMapLayerInfo objects')
    
    
    
    
    
    
    
    
       