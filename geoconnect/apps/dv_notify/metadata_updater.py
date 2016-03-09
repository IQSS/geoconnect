"""
Using the Dataverse APIs, add/update/delete
map metadata for a specified DataFile

Objects passed in for worldmap_layer_info include:

    - from apps.worldmap_connect.models import WorldMapLayerInfo
    - from apps.gis_tabular.models import WorldMapJoinLayerInfo, WorldMapLatLngInfo
"""
from __future__ import print_function

import os
import json
import requests # for POST

if __name__ == '__main__':
    import sys
    CURRENT_DIR = os.path.dirname(os.path.dirname(__file__))
    sys.path.append(os.path.join(CURRENT_DIR, '../../'))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geoconnect.settings.local")

#from geo_utils.key_checker import KeyChecker
from geo_utils.message_helper_json import MessageHelperJSON
from geo_utils.msg_util import msgt

from shared_dataverse_information.dataverse_info.url_helper import get_api_url_update_map_metadata,\
    get_api_url_delete_metadata

import logging
LOGGER = logging.getLogger('apps.dv_notify.metadata_updater')


class MetadataUpdater(object):
    """
    Send a metadata update to Dataverse.  Specifically, update the GIS Metadata block
    for a given file.
    """

    def __init__(self, dataverse_server_url, timeout_seconds=240, return_type_json=False):
        """
        Use data in a python dict to POST data to the Dataverse API,
        specifically the GeographicMetadataUpdateForm

        :param dv_metadata_params: dict containing information necessary for
        contacting dataverse
        """
        self.dataverse_server_url = dataverse_server_url
        self.timeout_seconds = timeout_seconds
        self.return_type_json = return_type_json

    def get_result_msg(self, success=False, user_msg='', data_dict=None):
        """
        Return a message in JSON format
        """
        if type(data_dict) is dict:
            print ('YES')
            d = MessageHelperJSON.get_dict_msg(success=success, msg=user_msg, data_dict=data_dict)
        else:
            d = MessageHelperJSON.get_dict_msg(success=success, msg=user_msg)

        if not self.return_type_json:
            return d

        return MessageHelperJSON.get_json_msg_from_dict(d)


    def delete_metadata_from_dataverse(self, worldmap_layer_info):
        """
        Delete map layer metadata from the Dataverse

        returns (True, None)
            or (False, 'error message of some type')
        """
        MetadataUpdater.check_for_required_methods(worldmap_layer_info)


        params = worldmap_layer_info.get_params_for_dv_delete_layer_metadata()
        api_delete_metadata_url = get_api_url_delete_metadata(self.dataverse_server_url)

        print ('params to send: %s' % params)
        print ('-' * 40)
        print ('update url: %s' % api_delete_metadata_url)
        print ('-' * 40)
        print ('payload: %s' % json.dumps(params))
        print ('-' * 40)

        req = None
        try:
            req = requests.post(api_delete_metadata_url,\
                    data=json.dumps(params),\
                    timeout=self.timeout_seconds)
        except requests.exceptions.Timeout:
            return (False, 'This request timed out.  (Time limit: %s seconds(s))'\
                % self.timeout_seconds)

        except requests.exceptions.ConnectionError as e:

            err_msg = '<p><b>Details for administrator:</b> Could not contact\
             the Dataverse server: %s</p><p>%s</p>'\
                                % (api_delete_metadata_url, e.message)
            LOGGER.error(err_msg)
            return (False, err_msg)

        msgt('text: %s' % req.text)
        msgt('status code: %s' % req.status_code)
        if req.status_code == 404:
            return (False, "The Dataverse delete API was not available")# 'Delete success')

        if req.status_code == 200:
            return (True, None)# 'Delete success')

        else:
            LOGGER.error('Metadata delete failed.  Status code: %s\nResponse:%s',\
             req.status_code, req.text)
            return (False, 'Sorry! The update failed.')

    @staticmethod
    def check_for_required_methods(worldmap_layer_info):
        """
        Make sure that the "worldmap_layer_info" has the required methods
        """
        assert worldmap_layer_info is not None,\
            "worldmap_layer_info cannot be None"

        assert hasattr(worldmap_layer_info, 'get_params_for_dv_update'),\
             "worldmap_layer_info must have a method get_params_for_dv_update()"\
             + " type: (%s)" % worldmap_layer_info

        assert hasattr(worldmap_layer_info, 'get_params_for_dv_delete_layer_metadata'),\
             "worldmap_layer_info must have a method get_params_for_dv_delete_layer_metadata()"\
             + " type: (%s)" % worldmap_layer_info

        assert hasattr(worldmap_layer_info, 'get_dataverse_server_url'),\
             "worldmap_layer_info must have a method get_dataverse_server_url()."\
             + " type: (%s)" % worldmap_layer_info


    def send_info_to_dataverse(self, worldmap_layer_info):
        """
        Go through the process of sending params to dataverse
        :param dv_metadata_params: python dict used to POST to dataverse
        :returns: JSON with "success" flag and either error or data
        :rtype: JSON string
        """
        #msgt('TURN THIS BACK ON!!!!')
        #return self.get_result_msg(True, '', data_dict={})

        MetadataUpdater.check_for_required_methods(worldmap_layer_info)

        LOGGER.info('send_params_to_dataverse')
        print('1) send_params_to_dataverse')

        dv_metadata_params = worldmap_layer_info.get_params_for_dv_update()
        print ('dv_metadata_params', dv_metadata_params)
        api_update_url = get_api_url_update_map_metadata(self.dataverse_server_url)

        print ('params to send: %s' % dv_metadata_params)
        print ('-' * 40)
        print ('update url: %s' % api_update_url)
        print ('-' * 40)
        print ('payload: %s' % json.dumps(dv_metadata_params))
        print ('-' * 40)

        req = None
        try:
            req = requests.post(api_update_url,\
                data=json.dumps(dv_metadata_params),\
                timeout=self.timeout_seconds)
        except requests.exceptions.Timeout:
            return self.get_result_msg(False,\
                'This request timed out.  (Time limit: %s seconds(s))'\
                % self.timeout_seconds)

        except requests.exceptions.ConnectionError as e:

            err_msg = '<p><b>Details for administrator:</b> Could not contact\
             the Dataverse server: %s</p><p>%s</p>'\
                                % (api_update_url, e.message)
            LOGGER.error(err_msg)
            return self.get_result_msg(False, err_msg)

        if not req.status_code == 200:

            print ('request text: %s' % req.text)

            LOGGER.error('Metadata update failed.  Status code: %s\nResponse:%s',\
                req.status_code, req.text)

            return self.get_result_msg(False, 'Sorry! The update failed.')

        print (req.text)
        dv_response_dict = req.json()
        print('4) req to json')

        print(dv_response_dict)
        if dv_response_dict.get('status', False) in ('OK', 'success'):
            dv_response_dict.pop('status')
            print('4) send result')
            return self.get_result_msg(True, '', data_dict=dv_response_dict)

        elif dv_response_dict.has_key('message'):
            return self.get_result_msg(False, dv_response_dict['message'])
        else:
            return self.get_result_msg(False, 'The import failed for an unknown reason')



    @staticmethod
    def delete_dataverse_map_metadata(worldmap_layer_info):
        """
        Via the Dataverse API, delete metadata for this map
        """
        MetadataUpdater.check_for_required_methods(worldmap_layer_info)

        LOGGER.info("delete_dataverse_map_metadata")

        #mu = MetadataUpdater(settings.DATAVERSE_SERVER_URL)
        mu = MetadataUpdater(worldmap_layer_info.get_dataverse_server_url())

        return mu.delete_metadata_from_dataverse(worldmap_layer_info)




    @staticmethod
    def update_dataverse_with_metadata(worldmap_layer_info):
        """
        Via the Dataverse API, update metadata for this Map
        """
        MetadataUpdater.check_for_required_methods(worldmap_layer_info)


        LOGGER.info("update_dataverse_with_metadata")
        #params_for_dv = worldmap_layer_info.get_params_for_dv_update()
        #mu = MetadataUpdater(settings.DATAVERSE_SERVER_URL)
        mu = MetadataUpdater(worldmap_layer_info.get_dataverse_server_url())

        resp_dict = mu.send_info_to_dataverse(worldmap_layer_info)
        if resp_dict.get('success', False) is True:
            return True
        return False


if __name__ == '__main__':
    pass
    #f2 = '../../scripts/worldmap_api/test_shps/poverty_1990_gfz.zip'


# ---------------------------
# shapefile related
# ---------------------------
"""
python manage.py shell
from django.conf import settings
from apps.dv_notify.metadata_updater import MetadataUpdater
from apps.worldmap_connect.models import WorldMapLayerInfo
wm_info = WorldMapLayerInfo.objects.first()
if wm_info is not None:
    mu = MetadataUpdater(settings.DATAVERSE_SERVER_URL)
    print (mu.send_info_to_dataverse(wm_info))
else:
    print('No WorldMapLayerInfo objects')
"""

# ---------------------------
# tabular related
# ---------------------------
"""
python manage.py shell
from django.conf import settings
from apps.dv_notify.metadata_updater import MetadataUpdater
from apps.gis_tabular.models import WorldMapJoinLayerInfo
wm_info = WorldMapJoinLayerInfo.objects.first()
if wm_info is not None:
    mu = MetadataUpdater(settings.DATAVERSE_SERVER_URL)
    print (mu.send_info_to_dataverse(wm_info))
else:
    print('No WorldMapLayerInfo objects')
"""
