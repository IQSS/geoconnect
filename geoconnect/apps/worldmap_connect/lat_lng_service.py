import logging
import requests

from django.conf import settings
from requests.exceptions import ConnectionError as RequestsConnectionError

from shared_dataverse_information.worldmap_api_helper.url_helper import MAP_LAT_LNG_TABLE_API_PATH

#from apps.gis_tabular.models import SimpleTabularTest   # for testing

LOGGER = logging.getLogger('apps.worldmap_connect.lat_lng_service')


def create_map_from_datatable_lat_lng(datatable_obj, lat_col, lng_col):
    """
    Use the WorldMap API to uplodat a datatable and join it to an existing layer
    """
    print 'create_map_from_datatable_lat_lng 1'
    if datatable_obj is None:
        return (False, 'The Tabular File object was not specified.')

    if lat_col is None:
        return (False, 'The Latitude column was not specified.')

    if lng_col is None:
        return (False, 'The Longitude column was not specified.')

    if not hasattr(datatable_obj, 'name'):
        return (False, 'The Tabular File object does not have a "name"')

    if not hasattr(datatable_obj, 'delimiter'):
        return (False, 'The Tabular File object does not have a "delimiter"')

    print 'create_map_from_datatable_lat_lng 2'

    # --------------------------------
    # Prepare parameters
    # --------------------------------
    map_params = dict(title=datatable_obj.name,
                    abstract="Abstract for ... {0}".format(datatable_obj.name),
                    delimiter=datatable_obj.delimiter,
                    lat_attribute=lat_col,
                    lng_attribute=lng_col)

    # --------------------------------
    # Prepare file
    # --------------------------------
    if not datatable_obj.dv_file or not datatable_obj.dv_file.path:
        return (False, "The file could not be found.")
    print 'create_map_from_datatable_lat_lng 3'

    files = {'uploaded_file': open(datatable_obj.dv_file.path,'rb')}

    print 'make request to', MAP_LAT_LNG_TABLE_API_PATH

    try:
        r = requests.post(MAP_LAT_LNG_TABLE_API_PATH,
                        data=map_params,
                        files=files,
                        auth=settings.WORLDMAP_ACCOUNT_AUTH,
                        timeout=30
                        )
    except RequestsConnectionError as e:
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

    if rjson.get('success', False) is True:
        return (True, rjson.get('message', '(no message sent)'))
    else:
        return (False, rjson.get('message', '(no message sent)'))
