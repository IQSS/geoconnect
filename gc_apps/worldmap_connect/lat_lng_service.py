import sys
import logging
import requests
import json
from django.conf import settings
from requests.exceptions import ConnectionError as RequestsConnectionError

from shared_dataverse_information.worldmap_api_helper.url_helper import MAP_LAT_LNG_TABLE_API_PATH
from gc_apps.gis_basic_file.dataverse_info_service import get_dataverse_info_dict

LOGGER = logging.getLogger('gc_apps.worldmap_connect.lat_lng_service')


def create_map_from_datatable_lat_lng(tabular_info, lat_col, lng_col):
    """
    Use the WorldMap API to uplodat a datatable and join it to an existing layer
    """
    LOGGER.debug('create_map_from_datatable_lat_lng 1')
    if tabular_info is None:
        return (False, 'The Tabular File object was not specified.')

    #if dataverse_metadata_dict is None:
    #    return (False, 'The Dataverse metadata was not specified.')

    if lat_col is None:
        return (False, 'The Latitude column was not specified.')

    if lng_col is None:
        return (False, 'The Longitude column was not specified.')

    if not hasattr(tabular_info, 'name'):
        return (False, 'The Tabular File object does not have a "name"')

    if not hasattr(tabular_info, 'delimiter'):
        return (False, 'The Tabular File object does not have a "delimiter"')

    print 'create_map_from_datatable_lat_lng 2'

    # --------------------------------
    # Prepare parameters
    # --------------------------------
    map_params = dict(title=tabular_info.name,
                    abstract=tabular_info.get_abstract_for_worldmap(),
                    delimiter=tabular_info.delimiter,
                    lat_attribute=lat_col,
                    lng_attribute=lng_col)
    #print json.dumps(map_params, indent=4)
    # Add dataverse dict info
    #
    dataverse_metadata_dict = get_dataverse_info_dict(tabular_info)
    map_params.update(dataverse_metadata_dict)

    print 'map_params', map_params

    # --------------------------------
    # Prepare file
    # --------------------------------
    if not tabular_info.dv_file:
        return (False, "The file could not be found.")

    print 'create_map_from_datatable_lat_lng 3'

    #files = {'uploaded_file': open(tabular_info.dv_file.path,'rb')}
    files = dict(uploaded_file=tabular_info.dv_file)

    print 'make request to', MAP_LAT_LNG_TABLE_API_PATH
    print '-' * 40

    try:
        r = requests.post(MAP_LAT_LNG_TABLE_API_PATH,
                        data=map_params,
                        files=files,
                        auth=settings.WORLDMAP_ACCOUNT_AUTH,
                        timeout=settings.WORLDMAP_DEFAULT_TIMEOUT
                        )
    except RequestsConnectionError as e:
        print 'err', e
        err_msg = 'Error connecting to WorldMap server: %s' % e.message
        LOGGER.error('Error trying to map lat/lng file with id: %s', datatable_obj.id )
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
        return (True, (rjson.get('message', '(no message sent)'), rjson))
        #return (True, (rjson.get('message', '(no message sent)'), rjson.get('data', {})))
    else:
        return (False, rjson.get('message', '(no message sent)'))
