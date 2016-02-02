import logging
import requests

from django.conf import settings
from requests.exceptions import ConnectionError as RequestsConnectionError

from shared_dataverse_information.worldmap_api_helper.url_helper import\
    MAP_LAT_LNG_TABLE_API_PATH,\
    UPLOAD_JOIN_DATATABLE_API_PATH
from apps.worldmap_connect.utils import get_latest_jointarget_information
#from apps.gis_tabular.models import SimpleTabularTest   # for testing

LOGGER = logging.getLogger('apps.worldmap_connect.join_layer_service')


def create_map_from_datatable_join(datatable_obj, dataverse_metadata_dict, table_attribute_for_join, target_layer_id):
    """
    Use the WorldMap API to uplodat a datatable and join it to an existing layer
    """
    print 'create_map_from_datatable_join 1'
    if datatable_obj is None:
        return (False, 'The Tabular File object was not specified.')

    if dataverse_metadata_dict is None:
        return (False, 'The Dataverse metadata was not specified.')

    if table_attribute_for_join is None:
        return (False, 'The join column was not specified.')

    if target_layer_id is None:
        return (False, 'The target layer was not specified.')

    if not hasattr(datatable_obj, 'name'):
        return (False, 'The target layer column was not specified')

    if not hasattr(datatable_obj, 'delimiter'):
        return (False, 'The Tabular File object does not have a "delimiter"')

    print 'create_map_from_datatable_join 2'

    # Based on the target layer ID,
    #   retrieve the layer name and column name
    join_target_info = get_latest_jointarget_information()
    (target_layer_name, target_column_name) = join_target_info.get_target_layer_name_column(target_layer_id)

    print 'target_layer_name', target_layer_name
    print 'target_column_name', target_column_name

    # --------------------------------
    # Prepare parameters
    # --------------------------------
    map_params = dict(title=datatable_obj.name,
                    abstract="Abstract for ... {0}".format(datatable_obj.name),
                    delimiter=datatable_obj.delimiter,
                    table_attribute=table_attribute_for_join,
                    layer_name=target_layer_name,
                    layer_attribute=target_column_name
                    )

    # Add dataverse dict info
    #
    map_params.update(dataverse_metadata_dict)

    print 'map_params', map_params

    # --------------------------------
    # Prepare file
    # --------------------------------
    if not datatable_obj.dv_file or not datatable_obj.dv_file.path:
        return (False, "The file could not be found.")
    print 'create_map_from_datatable_lat_lng 3'

    files = {'uploaded_file': open(datatable_obj.dv_file.path,'rb')}

    print 'make request to', UPLOAD_JOIN_DATATABLE_API_PATH
    print '-' * 40

    try:
        r = requests.post(UPLOAD_JOIN_DATATABLE_API_PATH,
                        data=map_params,
                        files=files,
                        auth=settings.WORLDMAP_ACCOUNT_AUTH,
                        timeout=30
                        )
    except RequestsConnectionError as e:
        print 'err', e
        err_msg = 'Error connecting to WorldMap server: %s' % e.message
        LOGGER.error('Error trying to join to datatable with id: %s', datatable_obj.id )
        LOGGER.error(err_msg)
        return (False, err_msg)
    except:
        err_msg = "Unexpected error: %s" % sys.exc_info()[0]
        LOGGER.error(err_msg)
        return (False, err_msg)

    try:
        rjson = r.json()
    except:
        return (False, "Sorry!  The mapping failed.  (%s)" % r.text)
    print rjson

    if rjson.get('success', False) is True:
        # (True, (message, data))
        return (True, rjson)
    else:
        return (False, rjson.get('message', '(no message sent)'))
