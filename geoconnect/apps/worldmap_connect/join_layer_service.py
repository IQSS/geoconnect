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
