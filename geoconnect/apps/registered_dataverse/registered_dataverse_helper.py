import sys
try:
    from urlparse import urlparse   # 2.x
except:
    from urllib.parse import urlparse   # 3.x

from apps.registered_dataverse.models import RegisteredDataverse
from geo_utils.msg_util import *

import logging
logger = logging.getLogger('registered_dataverse_helper')

def find_registered_dataverse(incoming_url):
    """
    Given a url, return a RegisteredDataverse object or None
    """
    assert incoming_url is not None, "incoming_url may not be None"

    try:
        r = urlparse(incoming_url)
    except:
        logger.info("Failed to parse incoming url: %s" % str(sys.exc_info()[0]) )
        return None
        
    if r.scheme and r.netloc:
        potential_dv_url = '://'.join([r.scheme, r.netloc]).lower()
        msg('potential_dv_url: %s' % potential_dv_url)
        try:
            return RegisteredDataverse.objects.get(dataverse_url=potential_dv_url, active=True)
        except RegisteredDataverse.DoesNotExist:
            logger.info("Failed to find RegisteredDataverse for url: %s (formatted: %s)" % (incoming_url, potential_dv_url))
            return None

    logger.info("Failed to parse incoming url: %s" % incoming_url)
    return None