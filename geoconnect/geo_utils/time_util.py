from datetime import datetime

TIME_FORMAT_STRING = '%Y-%m%d-%H%M'

def get_datetime_string_for_file():
    return datetime.now().strftime(TIME_FORMAT_STRING)
