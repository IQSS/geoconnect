import logging

logger = logging.getLogger(__name__)

def sizeof_fmt(num):
    if num is None:
        logger.error('Error: number for human readable filesize is "None"' % num)
        return None
                
    for x in ['bytes','KB','MB','GB','TB']:
        try:
            if num < 1024.0:
                return "%3.1f %s" % (num, x)
            num /= 1024.0
        except:
            logger.error('Error: could not convert %s to human readable filesize' % num)
            return None
            
    return None