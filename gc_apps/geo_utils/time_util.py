from datetime import datetime
from django.utils import timezone

TIME_FORMAT_STRING = '%Y-%m%d-%H%M'

def get_datetime_string_for_file():
    """Get datetime string for file naming"""
    return timezone.now().strftime(TIME_FORMAT_STRING)

def get_last_microsecond():
    """Used as a url param to clear any caching"""
    return datetime.now().microsecond

def get_last_microsecond_url_param():
    """Used as a url param to clear any caching"""
    return 'ts=%d' % datetime.now().microsecond
