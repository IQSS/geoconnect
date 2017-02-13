
FAILED_NOT_A_REGISTERED_DATAVERSE = 'FAILED_NOT_A_REGISTERED_DATAVERSE'

class ErrResultMsg:
    def __init__(self, err_type, err_msg):
        self.err_type = err_type
        self.err_msg = err_msg


def log_connect_error_message(error_message, logger=None, exception_obj=None):
    """Log a common ConnectionException message"""

    if logger:
        logger.error(error_message)

    if exception_obj:
        logger.error('Exception from : %s', exception_obj.__class__.__name__)
        if exception_obj.__dict__.has_key('message'):
            logger.error('Exception message : %s', exception_obj.message)
