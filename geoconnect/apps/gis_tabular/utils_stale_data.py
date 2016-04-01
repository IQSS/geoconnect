from datetime import datetime, timedelta

from apps.gis_tabular.models import TabularFileInfo # for testing
from apps.gis_tabular.models import WorldMapTabularLayerInfo,\
            WorldMapLatLngInfo, WorldMapJoinLayerInfo
from apps.worldmap_connect.models import WorldMapLayerInfo

DEFAULT_STALE_AGE = 3 * 60 * 60 # 3 hours, in seconds

def remove_stale_map_data(stale_age_in_seconds=DEFAULT_STALE_AGE):
    """
    Remove old map data...
    """
    current_time = datetime.now()

    for wm_info in WorldMapLatLngInfo.objects.all():
        remove_if_stale(wm_info, stale_age_in_seconds, current_time)

    for wm_info in WorldMapLatLngInfo.objects.all():
        remove_if_stale(wm_info, stale_age_in_seconds, current_time)

    for wm_info in WorldMapLayerInfo.objects.all():
        remove_if_stale(wm_info, stale_age_in_seconds, current_time)


def remove_if_stale(info_object, stale_age_in_seconds, current_time=None):
    assert hasattr(info_object, 'modified'),\
        'The info_object must have "modified" date'

    if not current_time:
        current_time = datetime.now()

    mod_time = info_object.modified
    if hasattr(mod_time, 'tzinfo'):
        mod_time = mod_time.replace(tzinfo=None)

    # Is this object beyond it's time limit
    time_diff = (current_time - mod_time).total_seconds()
    if time_diff > stale_age_in_seconds:
        # Yes! delete it
        print 'Removing: ', info_object
        info_object.delete()
"""
from apps.gis_tabular.utils_stale_data import *
remove_stale_map_data()
"""
