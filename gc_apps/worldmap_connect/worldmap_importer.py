from __future__ import print_function

import os
import requests     # http://docs.python-requests.org

if __name__ == '__main__':
    import sys
    CURRENT_DIR = os.path.dirname(os.path.dirname(__file__))
    sys.path.append(os.path.join(CURRENT_DIR, '../'))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geoconnect.settings")

from gc_apps.geo_utils.message_helper_json import MessageHelperJSON
from django.conf import settings

from shared_dataverse_information.worldmap_api_helper.url_helper import ADD_SHAPEFILE_API_PATH

from shared_dataverse_information.shapefile_import.forms import ShapefileImportDataForm
from shared_dataverse_information.shared_form_util.format_form_errors import format_errors_as_text

import logging
LOGGER = logging.getLogger('gc_apps.worldmap_connect.worldmap_importer')



class WorldMapImporter:
    """Attempts to create a WorldMap layer by sending over a shapefile
    and Dataverse related parameters

    Uses the WorldMap API described here:
        https://github.com/IQSS/geoconnect/blob/master/docs/api_worldmap_connect.md

    This is meant to be run asynchronously, thus the 4 minute timeout
    """
    def __init__(self, timeout_seconds=420, return_type_json=False):
        """
        :param worldmap_server_url: base server url, including http or
            https. e.g. http://worldmap.harvard.edu
        :type worldmap_server_url: str or unicode
        :param timeout_seconds: Optional. Number of seconds request is
            given until an exception is raised
        :type timeout_seconds: int or float
        """
        self.api_import_url = ADD_SHAPEFILE_API_PATH
        self.timeout_seconds = timeout_seconds
        self.return_type_json = return_type_json
        print ('WorldMapImporter. init.  api_import_url', self.api_import_url)

    def get_result_msg(self, success=False, msg='', data_dict=None):

        if isinstance(data_dict, dict):
            d = MessageHelperJSON.get_dict_msg(success=success, msg=msg, data_dict=data_dict)
        else:
            d = MessageHelperJSON.get_dict_msg(success=success, msg=msg)

        if not self.return_type_json:
            return d

        return MessageHelperJSON.get_json_msg_from_dict(d)

    def send_shapefile_to_worldmap(self, layer_params, file_object):
        """
        :param layer_params: Data to send in the POST. Example:
                 layer_params = {'title' : 'Boston Income'\
                        , 'abstract' : 'Shapefile containing Boston, MA income levels from 19xx'\
                        , 'email' : 'researcher@school.edu'\
                        , 'shapefile_name' : 'zipfile_name.zip'\
                        }
        :type layer_params
        :param fullpath_to_file: file name, including path, to shapefile in .zip format
        :type fullpath_to_file: str or unicode

        :returns: python dict with keys for "success" as well as messages, meteadata, etc.
                see https://github.com/IQSS/geoconnect/blob/master/docs/api_worldmap_connect.md
        :rtype: python dict
        """
        assert isinstance(layer_params, dict), "layer params must be a dict"

        print ('at final send: send_shapefile_to_worldmap')
        LOGGER.debug('send_shapefile_to_worldmap')

        # This validation should be fine.
        # The params are formatted using a ShapefileImportDataForm
        #
        validation_form = ShapefileImportDataForm(layer_params)
        if not validation_form.is_valid():
            form_errs_as_text = format_errors_as_text(validation_form)
            raise ValueError('layer_parms did not pass validation: \n%s' % form_errs_as_text)

        # Is the file available?
        #
        if file_object is None:
            err_msg = 'The file_object does not exist'
            LOGGER.error(err_msg)
            return self.get_result_msg(False, err_msg)

        shp_file_param = {'content': file_object}

        # Send the request to WorldMap
        #
        LOGGER.debug('import url: %s', self.api_import_url)
        LOGGER.debug('layer_params: %s', layer_params)
        LOGGER.debug ('self.timeout_seconds: %s', self.timeout_seconds)

        r = None
        try:
            r = requests.post(self.api_import_url,
                               data=layer_params,
                               files=shp_file_param,
                               auth=settings.WORLDMAP_ACCOUNT_AUTH,
                               timeout=settings.WORLDMAP_DEFAULT_TIMEOUT
                            )
        except requests.exceptions.ConnectionError as exception_obj:
            err_msg = """<br /><p><b>Details for administrator:</b> Could not contact the
                    WorldMap server: %s</p>"""\
                                % (self.api_import_url)
            LOGGER.error(err_msg)
            LOGGER.error('ConnectionError: %s', exception_obj.message)
            return self.get_result_msg(False, err_msg)

        except requests.exceptions.Timeout as e:
            err_msg = """Sorry! This request to the WorldMap server failed.
                    <p><b>Details for administrator:</b> Request to url %s timed out after %s seconds.</p>
                    <p>%s</p>"""\
                    % (self.api_import_url, self.timeout_seconds, e.message)

            LOGGER.error(err_msg)
            return self.get_result_msg(False, err_msg)

        if r.status_code == 200:
            wm_response_dict = r.json()
            LOGGER.debug('response: %s', wm_response_dict)
            if wm_response_dict.get('success', False) is True\
                and wm_response_dict.get('data') is not None:
                wm_response_dict.pop('success')
                return self.get_result_msg(True, '', data_dict=wm_response_dict.get('data'))

            elif wm_response_dict.has_key('message'):
                err_msgs = wm_response_dict['message']
                return self.get_result_msg(False, err_msgs)
        else:
            err_msg = "Request failed.  Status code: %s\n\n%s" % (r.status_code, r.text)
            return self.get_result_msg(False, err_msg)




        return self.get_result_msg(False, 'The import failed for an unknown reason')




if __name__ == '__main__':

    f2 = '../../scripts/worldmap_api/test_shps/poverty_1990_gfz.zip'
    wmi = WorldMapImporter()

    '''
    {u'layer_link': u'http://localhost:8000/data/geonode:poverty_1990_gfz_zip_vqs', u'worldmap_username': u'raman_prasad', u'layer_name': u'geonode:poverty_1990_gfz_zip_vqs', u'success': True, u'embed_map_link': u'http://localhost:8000/maps/embed/?layer=geonode:poverty_1990_gfz_zip_vqs'}
    '''

    params1 = {'title' : 'Boston Income'\
            , 'abstract' : '[test] Shapefile containing Boston, MA income levels from 19xx'\
            , 'email' : 'raman_prasad@harvard.edu'\
            , 'shapefile_name' : 'income_in_boston_gui.zip'\
            }
    #income data from 1990 census
    wmi = WorldMapImporter()
    f1 = '../scripts/worldmap_api/test_shps/income_in_boston_gui.zip'
    wmi.send_shapefile_to_worldmap(params1, f1)
    """
    #payload = {'key1': 'value1', 'key2': 'value2'}
    #>>> r = requests.post("http://httpbin.org/post", data=payload)
    #>>> print r.text
    """
