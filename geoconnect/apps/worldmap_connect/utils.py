"""
Convenience methods for using the WorldMap API
"""
from django.utils import timezone
from apps.worldmap_connect.models import JoinTargetInformation
from apps.worldmap_connect.dataverse_layer_services import get_join_targets
from datetime import timedelta
import logging

LOGGER = logging.getLogger('apps.worldmap_connect.utils')

JOIN_TARGET_UPDATE_TIME = 10 * 60 # 10 minutes



def get_latest_jointarget_information():
    """
    Retrieve recent JoinTarget Information from the database.

    If recent information is not available, use the WorldMap API and store
    the new information in the db.
    """

    # ---------------------------------
    # (1) Is available JoinTarget info from db 
    # ---------------------------------
    recent_time_window = timezone.now() + timedelta(seconds=(-1 * JOIN_TARGET_UPDATE_TIME))

    joint_target = JoinTargetInformation.objects.filter(created__gte=recent_time_window\
                    ).first()
    if joint_target is not None:
        return joint_target

    # ---------------------------------
    # (2) Get JoinTarget info from the WorldMap API
    #   and save it to the database
    # ---------------------------------
    (success, dict_info_or_err) = get_join_targets()
    if success:
        joint_target = JoinTargetInformation(name=timezone.now().strftime("%Y-%m-%d %H:%M:%S"),\
                target_info=dict_info_or_err)
        joint_target.save()
        return joint_target

    # ---------------------------------
    # (3) Get JoinTarget info from database --
    #   even if it's old
    # ---------------------------------
    joint_target = JoinTargetInformation.objects.first()
    if joint_target is None:
        LOGGER.error('No JoinTargetInformation available in the database \
        (failed attempt to retrieve it from WorldMap): %s', dict_info_or_err)
        return None

    LOGGER.error('Failed to retrieve timely JoinTargetInformation from WorldMap\
     (used last avaialable from the database): %s', dict_info_or_err)

    return joint_target

def get_geocode_types_and_join_layers():
    """
    Used for the the join layer form.

    Return lists of:
        - geocode types   [(id, description), (id, description)...]
        - available layers  [(id, description), (id, description)...]
    """
    # Retrieve a JoinTarget object
    join_target_info = get_latest_jointarget_information()
    if join_target_info is None:
        LOGGER.error("Could not retrieve join target information")
        return (None, None)

    return (join_target_info.get_geocode_types(),\
        join_target_info.get_available_layers_list())


"""
python manage.py shell
from apps.worldmap_connect.utils import get_latest_jointarget_information
jt = get_latest_jointarget_information()
jt.get_geocode_types()
"""
