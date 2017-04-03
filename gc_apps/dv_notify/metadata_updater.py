"""
Using the Dataverse APIs, add/update/delete
map metadata for a specified DataFile

Objects passed in for worldmap_layer_info include:

    - from gc_apps.gis_shapefiles.models import WorldMapShapefileLayerInfo
    - from gc_apps.gis_tabular.models import WorldMapJoinLayerInfo, WorldMapLatLngInfo
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

from gc_apps.geo_utils.message_helper_json import MessageHelperJSON
from gc_apps.geo_utils.msg_util import msgt
from gc_apps.geo_utils.error_result_msg import log_connect_error_message


from shared_dataverse_information.dataverse_info.url_helper import get_api_url_update_map_metadata,\
    get_api_url_delete_metadata

import logging
LOGGER = logging.getLogger('gc_apps.dv_notify.metadata_updater')

EMBED_MAP_LINK_KEY = 'embedMapLink'

ERROR_DV_NO_SERVER_RESPONSE = 'Could not contact the Dataverse server:'
ERROR_DV_PAGE_NOT_FOUND = 'Dataverse page not found:'
ERROR_DV_METADATA_UPDATE = 'Error updating the Dataverse metadata.'

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
            msg_dict = MessageHelperJSON.get_dict_msg(\
                        success=success,
                        msg=user_msg,
                        data_dict=data_dict)
        else:
            msg_dict = MessageHelperJSON.get_dict_msg(\
                        success=success,
                        msg=user_msg)

        if not self.return_type_json:
            return msg_dict

        return MessageHelperJSON.get_json_msg_from_dict(msg_dict)


    def delete_metadata_from_dataverse(self, worldmap_layer_info):
        """
        Delete map layer metadata from the Dataverse

        returns (True, None)
            or (False, 'error message of some type')
        """
        MetadataUpdater.check_for_required_methods(worldmap_layer_info)


        params = worldmap_layer_info.get_params_for_dv_delete_layer_metadata()
        api_delete_metadata_url = get_api_url_delete_metadata(self.dataverse_server_url)

        """
        print ('params to send: %s' % params)
        print ('-' * 40)
        print ('update url: %s' % api_delete_metadata_url)
        print ('-' * 40)
        print ('payload: %s' % json.dumps(params))
        print ('-' * 40)
        """

        req = None
        try:
            req = requests.post(api_delete_metadata_url,\
                    data=json.dumps(params),\
                    timeout=self.timeout_seconds)
        except requests.exceptions.Timeout:
            return (False, 'This request timed out.  (Time limit: %s seconds(s))'\
                % self.timeout_seconds)

        except requests.exceptions.ConnectionError as exception_obj:
            err_msg = ('%s %s') % (ERROR_DV_NO_SERVER_RESPONSE, api_delete_metadata_url)

            log_connect_error_message(err_msg, LOGGER, exception_obj)

            return (False, err_msg)


        #msgt('status code/text: %s/%s' % (\
        #                        req.status_code,
        #                        req.text.encode('utf-8'))

        if req.status_code == 404:
            return (False,\
                    '%s %s' % (ERROR_DV_PAGE_NOT_FOUND, api_delete_metadata_url))

        if req.status_code == 200:
            return (True, None)# 'Delete success')

        else:
            # See if an error message was sent back...
            error_msg = None
            try:
                dv_response_dict = req.json()
                if dv_response_dict.has_key('message'):
                    error_msg = dv_response_dict['message']
            except:
                LOGGER.error('Metadata update failed.  Status code: %s\nResponse:%s',\
                    req.status_code, req.text.encode('utf-8'))

            if error_msg is None:
                error_msg = 'Sorry! The update failed.'

            LOGGER.error('Status code: %s\nError message:%s',\
                req.status_code, error_msg)

            return (False, error_msg)


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


    def update_embed_link_for_https(self, params):
        """
        Force the embed map link to https
        """
        if params is None or EMBED_MAP_LINK_KEY not in params:
            return False

        embed_link_val = params[EMBED_MAP_LINK_KEY].lower()
        if embed_link_val.find('worldmap.harvard.edu') > -1:
            if embed_link_val.startswith('http://'):
                embed_link_val = embed_link_val.replace('http:', 'https:', 1)
                params[EMBED_MAP_LINK_KEY] = embed_link_val
                return True

        return True


    def send_info_to_dataverse(self, worldmap_layer_info):
        """
        Go through the process of sending params to dataverse
        :param dv_metadata_params: python dict used to POST to dataverse
        :returns: JSON with "success" flag and either error or data
        :rtype: JSON string
        """
        MetadataUpdater.check_for_required_methods(worldmap_layer_info)

        dv_metadata_params = worldmap_layer_info.get_params_for_dv_update()
        self.update_embed_link_for_https(dv_metadata_params)

        #print ('dv_metadata_params', dv_metadata_params)

        # FIXME: temp fix for DV error
        # Make joinDescription an empty String instead of None
        if dv_metadata_params.get('joinDescription', None) is None:
            dv_metadata_params['joinDescription'] = ''

        api_update_url = get_api_url_update_map_metadata(self.dataverse_server_url)

        #print ('params to send: %s' % dv_metadata_params)
        #print ('-' * 40)
        print ('update url: %s' % api_update_url)
        #print ('-' * 40)
        #print ('payload: %s' % json.dumps(dv_metadata_params))
        #print ('-' * 40)

        req = None
        try:
            req = requests.post(api_update_url,\
                data=json.dumps(dv_metadata_params),\
                timeout=self.timeout_seconds)
        except requests.exceptions.Timeout:
            return self.get_result_msg(False,\
                'This request timed out.  (Time limit: %s seconds(s))'\
                % self.timeout_seconds)

        except requests.exceptions.ConnectionError as exception_obj:

            err_msg = ('%s %s') % (ERROR_DV_NO_SERVER_RESPONSE, api_update_url)

            log_connect_error_message(err_msg, LOGGER, exception_obj)

            return self.get_result_msg(False, err_msg)


        if req.status_code == 404:

            LOGGER.error('Metadata update failed.  Page not found: %s',\
                api_update_url)

            return self.get_result_msg(\
                    False,
                    '%s %s' % (ERROR_DV_PAGE_NOT_FOUND, api_update_url))

        elif not req.status_code == 200:

            # See if an error message was sent back...
            error_msg = None
            try:
                dv_response_dict = req.json()
                if dv_response_dict.has_key('message'):
                    error_msg = dv_response_dict['message']
            except:
                LOGGER.error('Metadata update failed.  Status code: %s\nResponse:%s',\
                    req.status_code, req.text.encode('utf-8'))

            if error_msg is None:
                error_msg = '%s (status code: %s)<br />endpoint: %s' % (\
                                ERROR_DV_METADATA_UPDATE,
                                req.status_code,
                                api_update_url)

            return self.get_result_msg(False, error_msg)

        dv_response_dict = req.json()

        if dv_response_dict.get('status', False) in ('OK', 'success'):
            dv_response_dict.pop('status')
            #print('4) send result')
            return self.get_result_msg(True, '', data_dict=dv_response_dict)

        elif dv_response_dict.has_key('message'):
            return self.get_result_msg(False, dv_response_dict['message'])
        else:
            return self.get_result_msg(False, 'The import failed for an unknown reason')



    @staticmethod
    def delete_dataverse_map_metadata(worldmap_layer_info, custom_dataverse_url=None):
        """
        Via the Dataverse API, delete metadata for this map
        """
        MetadataUpdater.check_for_required_methods(worldmap_layer_info)

        LOGGER.info("delete_dataverse_map_metadata")

        if custom_dataverse_url:
            metadata_updater = MetadataUpdater(custom_dataverse_url)
        else:
            metadata_updater = MetadataUpdater(worldmap_layer_info.get_dataverse_server_url())

        return metadata_updater.delete_metadata_from_dataverse(worldmap_layer_info)




    @staticmethod
    def update_dataverse_with_metadata(worldmap_layer_info, custom_dataverse_url=None):
        """
        Via the Dataverse API, update metadata for this Map
        custom_dataverse_url = Optional. Dataverse server url.
            - Usually this info taken from the worldmap_layerinfo object
        """
        MetadataUpdater.check_for_required_methods(worldmap_layer_info)


        LOGGER.info("update_dataverse_with_metadata")

        if custom_dataverse_url:
            metadata_updater = MetadataUpdater(custom_dataverse_url)
        else:
            metadata_updater = MetadataUpdater(worldmap_layer_info.get_dataverse_server_url())

        resp_dict = metadata_updater.send_info_to_dataverse(worldmap_layer_info)

        if resp_dict.get('success', False) is True:
            return True, resp_dict
        return False, resp_dict


if __name__ == '__main__':
    pass
    #f2 = '../../scripts/worldmap_api/test_shps/poverty_1990_gfz.zip'


# ---------------------------
# tabular related
# ---------------------------
"""
python manage.py shell
from django.conf import settings
from gc_apps.dv_notify.metadata_updater import MetadataUpdater
from gc_apps.gis_tabular.models import WorldMapJoinLayerInfo
wm_info = WorldMapJoinLayerInfo.objects.first()
if wm_info is not None:
    mu = MetadataUpdater(settings.DATAVERSE_SERVER_URL)
    print (mu.send_info_to_dataverse(wm_info))
else:
    print('No WorldMapJoinLayerInfo objects')
"""
