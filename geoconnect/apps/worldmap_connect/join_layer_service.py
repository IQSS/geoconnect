import logging
import requests
import sys

from django.conf import settings
from requests.exceptions import ConnectionError as RequestsConnectionError

from geo_utils.msg_util import msg, msgt

from shared_dataverse_information.worldmap_api_helper.url_helper import\
    MAP_LAT_LNG_TABLE_API_PATH,\
    UPLOAD_JOIN_DATATABLE_API_PATH,\
    GET_TABLEJOIN_INFO
from apps.worldmap_connect.utils import get_latest_jointarget_information
#from apps.gis_tabular.models import SimpleTabularTest   # for testing

LOGGER = logging.getLogger('apps.worldmap_connect.join_layer_service')


def get_tablejoin_info(tablejoin_id):
    """
    Use the WorldMap API to retrieve TableJoin data

    from apps.worldmap_connect.join_layer_service import get_tablejoin_info
    get_tablejoin_info(215)
    """
    if not tablejoin_id:
        LOGGER.error('A tablejoin_id was not specified')
        return (False, 'You must specifiy a tablejoin_id')

    api_url = '%s%s/' % (GET_TABLEJOIN_INFO, tablejoin_id)
    msg('api_url: %s' % api_url)

    try:
        r = requests.get(api_url,
                        auth=settings.WORLDMAP_ACCOUNT_AUTH,
                        timeout=settings.WORLDMAP_SHORT_TIMEOUT
                        )
    except RequestsConnectionError as e:
        print 'err', e
        err_msg = 'Error connecting to WorldMap server: %s' % e.message
        LOGGER.error('Error trying to retrive TableJoin with id: %s', tablejoin_id)
        LOGGER.error(err_msg)
        return (False, err_msg)
    except:
        err_msg = "Unexpected error: %s" % sys.exc_info()[0]
        LOGGER.error(err_msg)
        return (False, err_msg)

    msg(r.text)
    try:
        rjson = r.json()
    except TypeError:
        return (False, "Sorry!  Could not retrieve the TableJoin information.  (%s)" % r.text)

    if rjson.get('success', False) is True:
        return (True, rjson)
    else:
        return (False, rjson.get('message', '(no message sent)'))


class TableJoinMapMaker(object):
    """
    Use the WorldMap API to uplodat a datatable and join it to an existing layer
    """

    def __init__(self, datatable_obj, dataverse_metadata_dict,\
        table_attribute_for_join, target_layer_id):
        self.datatable_obj = datatable_obj
        self.dataverse_metadata_dict = dataverse_metadata_dict
        self.table_attribute_for_join = table_attribute_for_join
        self.target_layer_id = target_layer_id

        self.err_found = False
        self.err_messages = []

        self.rjson_output = None

        self.sanity_check()
        #self.run_map_create()

    def get_map_info(self):
        return self.rjson_output

    def add_error(self, err_msg):
        """
        Error detected, store a messsage in the class
        """
        if err_msg is None:
            return
        self.err_found = True
        self.err_messages.append(err_msg)

    def get_error_msg(self):
        return '\n'.join(self.err_messages)

    def sanity_check(self):

        if self.datatable_obj is None:
            self.add_error('The Tabular File object was not specified.')

        if self.dataverse_metadata_dict is None:
            self.add_error('The Dataverse metadata was not specified.')

        if self.table_attribute_for_join is None:
            self.add_error('The join column was not specified.')

        if self.target_layer_id is None:
            self.add_error('The target layer was not specified.')

        if not hasattr(self.datatable_obj, 'name'):
            self.add_error('The target layer column was not specified')

        if not hasattr(self.datatable_obj, 'delimiter'):
            self.add_error('The Tabular File object does not have a "delimiter"')


    def run_map_create(self):
        msg('create_map_from_datatable_join 1')

        # Based on the target layer ID,
        #   retrieve the layer name and column name
        join_target_info = get_latest_jointarget_information()

        (target_layer_name, target_column_name) = join_target_info.get_target_layer_name_column(self.target_layer_id)

        msg('target_layer_name: %s' % target_layer_name)
        msg('target_column_name: %s' % target_column_name)

        # --------------------------------
        # Prepare parameters
        # --------------------------------
        map_params = dict(title=self.datatable_obj.name,
                        abstract="Abstract for ... {0}".format(self.datatable_obj.name),
                        delimiter=self.datatable_obj.delimiter,
                        table_attribute=self.table_attribute_for_join,
                        layer_name=target_layer_name,
                        layer_attribute=target_column_name
                        )

        # Add dataverse dict info
        #
        map_params.update(self.dataverse_metadata_dict)

        msg('map_params: %s' % map_params)

        # --------------------------------
        # Prepare file
        # --------------------------------
        if not self.datatable_obj.dv_file or not self.datatable_obj.dv_file.path:
            self.add_error("The file could not be found.")
            return False

        msg('create_map_from_datatable_join 3')

        files = {'uploaded_file': open(self.datatable_obj.dv_file.path,'rb')}

        print 'make request to', UPLOAD_JOIN_DATATABLE_API_PATH
        print '-' * 40

        try:
            r = requests.post(UPLOAD_JOIN_DATATABLE_API_PATH,
                            data=map_params,
                            files=files,
                            auth=settings.WORLDMAP_ACCOUNT_AUTH,
                            timeout=settings.WORLDMAP_DEFAULT_TIMEOUT
                            )
        except RequestsConnectionError as e:
            print 'err', e
            err_msg = 'Error connecting to WorldMap server: %s' % e.message
            LOGGER.error('Error trying to join to datatable with id: %s', datatable_obj.id )
            LOGGER.error(err_msg)
            self.add_error(err_msg)
            return False
        except:
            err_msg = "Unexpected error: %s" % sys.exc_info()[0]
            LOGGER.error(err_msg)
            self.add_error(err_msg)
            return False

        try:
            rjson = r.json()
        except:
            self.add_error("Sorry!  The mapping failed.  (%s)" % r.text)
            return False
        msg('rjson: %s' % rjson)

        if rjson.get('success', False) is True:
            self.rjson_output = rjson
            # (True, (message, data))
            return True
        else:
            self.add_error(rjson.get('message', '(no message sent)'))
            return False
