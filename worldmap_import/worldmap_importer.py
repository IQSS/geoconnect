from __future__ import print_function
"""import itertools
import mimetypes
import mimetools

from cStringIO import StringIO
import urllib
import urllib2
import json
"""
import os
import requests
import timeit
import json
try:
    from test_token import DVN_TOKEN, WORLDMAP_SERVER_URL
except:
    DVN_TOKEN = 'fake-key'
    WORLDMAP_SERVER_URL = 'tserver.need-name.edu'

def get_json_str_msg(success=False, msg=''):
    return { 'success': success\
            , 'message' : msg \
            }
            
class WorldMapImporter:
    """
    Attempts to create a WorldMap layer by sending over a shapefile and Dataverse related parameters 

    Uses the WorldMap API described here: 
        https://github.com/IQSS/geoconnect/blob/master/docs/api_worldmap_import.md

   
    """
    IMPORT_API_PATH = 'dvn/import'
    REQUIRED_PARAM_KEYS = ['title', 'abstract', 'email', 'shapefile_name', 'geoconnect_token']
    def __init__(self):
        self.import_url = os.path.join(WORLDMAP_SERVER_URL, self.IMPORT_API_PATH)

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
        
        if not all(pkey in layer_params for pkey in REQUIRED_PARAM_KEYS):
            missing_keys = [not pkey in layer_params for pkey in REQUIRED_PARAM_KEYS]
            missing_keys = [str(k) for k in missing_keys]
            key_str = ', '.join(missing_keys)
            return get_json_str_msg(False, 'These parameters are missing from "layer_params": %s' % key_str)
        if not os.path.isfile(fullpath_to_file):
            return get_json_str_msg(False, 'This file does not exist: %s' % fullpath_to_file)
                
        print(self.import_url)
        #return
        #params = { 'key1' : 'ha' }
        #payload = {'key1': 'value1', 'key2': 'value2'}
        shp_file_param = {'content': open(fullpath_to_file, 'rb')}
        req = requests.post(self.import_url, data=layer_params, files=shp_file_param)
        print (req.text)
    
    def send_shapefile_to_worldmap2(self, title, abstract, fullpath_to_file, email='raman_prasad@harvard.edu'):
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
            return get_json_str_msg(False, 'A title is required')
        if abstract is None or len(abstract.strip())== 0:
            return get_json_str_msg(False, 'An abstract is required')
        if email is None or len(email.strip())== 0:
            return get_json_str_msg(False, 'An email is required')
        if not os.path.isfile(fullpath_to_file):
            return get_json_str_msg(False, 'This file does not exist: %s' % fullpath_to_file)
            
        shapefile_name = os.path.basename(fullpath_to_file)
        params = {'title' : title\
                , 'abstract' : abstract\
                , 'email' : email\
                , 'shapefile_name' : shapefile_name\
                , 'geoconnect_token' : DVN_TOKEN\
                }

        return self.send_shapefile_to_worldmap(params, fullpath_to_file)
        
        
if __name__ == '__main__':
    f1 = '../scripts/worldmap_api/test_shps/blah.zip'
    wmi = WorldMapImporter()
    print( wmi.send_shapefile_to_worldmap2('St Louis income 1990', 'St. Louis data', f1))
    
    #f2 = '../scripts/worldmap_api/test_shps/poverty_1990_gfz.zip'
    #wmi = WorldMapImporter()
    #wmi.send_shapefile_to_worldmap2('St Louis income 1990', 'St. Louis data', f2)
    
    """
    
    params1 = {'title' : 'Boston Income'\
            , 'abstract' : '[test] Shapefile containing Boston, MA income levels from 19xx'\
            , 'email' : 'raman_prasad@harvard.edu'\
            , 'shapefile_name' : 'income_in_boston_gui.zip'\
            , 'geoconnect_token' : DVN_TOKEN\
            }
             income data from 1990 census 
    wmi = WorldMapImporter()
    f1 = '../scripts/worldmap_api/test_shps/income_in_boston_gui.zip'
    wmi.send_shapefile_to_worldmap(params1, f1)
    """
    #payload = {'key1': 'value1', 'key2': 'value2'}
    #>>> r = requests.post("http://httpbin.org/post", data=payload)
    #>>> print r.text
                     
                
                
                