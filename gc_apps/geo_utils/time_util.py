from django.utils import timezone

TIME_FORMAT_STRING = '%Y-%m%d-%H%M'

def get_datetime_string_for_file():
    return timezone.now().strftime(TIME_FORMAT_STRING)
