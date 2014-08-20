from __future__ import print_function

import os
import requests     # http://docs.python-requests.org

if __name__=='__main__':
    import sys
    CURRENT_DIR = os.path.dirname(os.path.dirname(__file__))
    sys.path.append(os.path.join(CURRENT_DIR, '../'))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geoconnect.settings")

from geo_utils.key_checker import KeyChecker
from geo_utils.json_field_reader import MessageHelperJSON
from django.conf import settings
"""
try:
    from test_token import WORLDMAP_TOKEN_FOR_DV, WORLDMAP_SERVER_URL
except:
    WORLDMAP_TOKEN_FOR_DV = 'fake-key'
    WORLDMAP_SERVER_URL = 'http://worldmap-fake-url.harvard.edu'
"""
import logging
logger = logging.getLogger(__name__)



class WorldMapImporter:
    """
    Attempts to create a WorldMap layer by sending over a shapefile and Dataverse related parameters 

    Uses the WorldMap API described here: 
        https://github.com/IQSS/geoconnect/blob/master/docs/api_worldmap_import.md

    This is meant to be run asynchronously, thus the 4 minute timeout
    """
    IMPORT_API_PATH = 'dvn/import'
    REQUIRED_PARAM_KEYS = ['title', 'abstract', 'email', 'shapefile_name', 'geoconnect_token']
    
    def __init__(self, worldmap_server_url, timeout_seconds=240, return_type_json=False):
        """
        :param worldmap_server_url: base server url, including http or https. e.g. http://worldmap.harvard.edu
        :type worldmap_server_url: str or unicode
        :param timeout_seconds: Optional. Number of seconds request is given until an exception is raised
        :type timeout_seconds: int or float
        """
        self.api_import_url = os.path.join(worldmap_server_url, self.IMPORT_API_PATH)
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
    
    def send_shapefile_to_worldmap(self, layer_params, fullpath_to_file):
        """
        :param layer_params: Data to send in the POST. Example:
                 layer_params = {'title' : 'Boston Income'\
                        , 'abstract' : 'Shapefile containing Boston, MA income levels from 19xx'\
                        , 'email' : 'researcher@school.edu'\
                        , 'shapefile_name' : 'zipfile_name.zip'\
                        , 'geoconnect_token' : 'token-for-api-use'\
                        }
        :type layer_params: python dictionary
        :param fullpath_to_file: file name, including path, to shapfile in .zip format
        :type fullpath_to_file: str or unicode
        
        :returns: python dict with keys for "success" as well as messages, meteadata, etc.  
                see https://github.com/IQSS/geoconnect/blob/master/docs/api_worldmap_import.md
        :rtype: python dict
        """
        
        #
        #   (1) Make sure that the required parameters are there
        #
        logger.debug('send_shapefile_to_worldmap')
        if not type(layer_params) is dict:  
            err_msg = 'The shapefile metadata (title, abstract, etc.) was not found. '
            logger.error(err_msg + 'layer_params is type: %s' % (layer_params.__class__.__name__) )
            return self.get_result_msg(False, err_msg)

        # Is the file available?
        #
        if fullpath_to_file is None or not os.path.isfile(fullpath_to_file):
            err_msg = 'This file does not exist: %s' % fullpath_to_file
            logger.error(err_msg)
            return self.get_result_msg(False, err_msg)
        
        # Set the dv auth token
        layer_params['geoconnect_token'] = settings.WORLDMAP_TOKEN_FOR_DV
        
        # Check for required keys -- replace this with a form!!
        key_check_response = KeyChecker.has_required_keys(self.REQUIRED_PARAM_KEYS, layer_params)        
        if not key_check_response.success:
            logger.error(key_check_response.err_msg + ' Info not in "layer_params"')
            return self.get_result_msg(key_check_response.err_msg)

        #
        #   Prepare the actual file to send to WorldMap
        #
        shp_file_param = {'content': open(fullpath_to_file, 'rb')}

       
        # Send the request to WorldMap
        #
        try:
            logger.debug('import url: %s' % self.api_import_url)
            
            logger.debug('layer_params: %s' % layer_params)
            req = requests.post(self.api_import_url, data=layer_params, files=shp_file_param, timeout=self.timeout_seconds)
            wm_response_dict = req.json()
            logger.debug('response: %s' % wm_response_dict)
            if wm_response_dict.get('success', False) is True and wm_response_dict.get('data') is not None:
                wm_response_dict.pop('success')
                return self.get_result_msg(True, '', data_dict=wm_response_dict.get('data'))
                                
            elif wm_response_dict.has_key('message'):
                msg = wm_response_dict['message']
                return self.get_result_msg(False, msgs)
                
        except requests.exceptions.Timeout:
            return self.get_result_msg(False, 'This request timed out.  (Time limit: %s seconds(s))' % self.timeout_seconds)
        except:
            return self.get_result_msg(False, 'Sorry! The request failed')
            
            
        return self.get_result_msg(False, 'The import failed for an unknown reason')
        
         
    def send_shapefile_to_worldmap2(self, title, abstract, fullpath_to_file, email):
        """Alternative function for "send_shapefile_to_worldmap"
        Prepares the python dictionary of layer_params and calls usual function for "send_shapefile_to_worldmap"
        
        :param title: Layer title
        :type title: str or unicode
        :param abstract: Layer title
        :type abstract: str or unicode
        :param fullpath_to_file: file name, including path, to shapfile in .zip format
        :type fullpath_to_file: str or unicode
        :param email: Email address of DV User
        :type email: str or unicode in email format
        
        :returns: python dict with keys for "success" as well as messages, meteadata, etc.  
                see https://github.com/IQSS/geoconnect/blob/master/docs/api_worldmap_import.md
        :rtype: python dict
        """
        if title is None or len(title.strip())== 0:
            return self.get_result_msg(False, 'A title is required')
        if abstract is None or len(abstract.strip())== 0:
            return self.get_result_msg(False, 'An abstract is required')
        if email is None or len(email.strip())== 0:
            return self.get_result_msg(False, 'An email is required')
        if not os.path.isfile(fullpath_to_file):
            return self.get_result_msg(False, 'This file does not exist: %s' % fullpath_to_file)
            
        shapefile_name = os.path.basename(fullpath_to_file)
        params = {'title' : title\
                , 'abstract' : abstract\
                , 'email' : email\
                , 'shapefile_name' : shapefile_name\
                , 'geoconnect_token' : settings.WORLDMAP_TOKEN_FOR_DV\
                }

        return self.send_shapefile_to_worldmap(params, fullpath_to_file)
        
        
if __name__ == '__main__':
    """
    f1 = '../scripts/worldmap_api/test_shps/blah.zip'
    wmi = WorldMapImporter(WORLDMAP_SERVER_URL)
    print( wmi.send_shapefile_to_worldmap2('St Louis income 1990', 'St. Louis data', f1, 'raman_prasad@harvard.edu'))
    """
    f2 = '../../scripts/worldmap_api/test_shps/poverty_1990_gfz.zip'
    wmi = WorldMapImporter(settings.WORLDMAP_SERVER_URL)
    
    print (wmi.send_shapefile_to_worldmap2('St Louis income 1990', 'St. Louis data', f2, 'raman_prasad@harvard.edu'))
    #{u'layer_link': u'http://localhost:8000/data/geonode:poverty_1990_gfz_zip_vqs', u'worldmap_username': u'raman_prasad', u'layer_name': u'geonode:poverty_1990_gfz_zip_vqs', u'success': True, u'embed_map_link': u'http://localhost:8000/maps/embed/?layer=geonode:poverty_1990_gfz_zip_vqs'}
    """
    
    params1 = {'title' : 'Boston Income'\
            , 'abstract' : '[test] Shapefile containing Boston, MA income levels from 19xx'\
            , 'email' : 'raman_prasad@harvard.edu'\
            , 'shapefile_name' : 'income_in_boston_gui.zip'\
            }
             income data from 1990 census 
    wmi = WorldMapImporter()
    f1 = '../scripts/worldmap_api/test_shps/income_in_boston_gui.zip'
    wmi.send_shapefile_to_worldmap(params1, f1)
    """
    #payload = {'key1': 'value1', 'key2': 'value2'}
    #>>> r = requests.post("http://httpbin.org/post", data=payload)
    #>>> print r.text
                     
                
                
                