"""
Set attributes used for nearly all views
"""
from django.conf import settings

from gc_apps.geo_utils.geoconnect_step_names import GEOCONNECT_STEPS,\
    STEP1_EXAMINE, STEP2_STYLE

def get_common_lookup(request, **kwargs):
    """
    Return dict with attributes common to nearly all views
    """
    if request is None:
        return {}

    if request.user and request.user.is_active and request.user.is_staff:
        is_staff = True
    else:
        is_staff = False

    is_superuser = False
    if request.user and request.user.is_authenticated():
        is_logged_in = True
        if request.user.is_superuser:
            is_superuser = True
    else:
        is_logged_in = False


    current_url = '{0}{1}'.format(request.get_host(), request.get_full_path())

    common_dict = dict(DATAVERSE_SERVER_URL=settings.DATAVERSE_SERVER_URL,\
            current_url=current_url,\
            DEBUG_MODE=settings.DEBUG,\
            GEOCONNECT_STEPS=GEOCONNECT_STEPS,\
            STEP1_EXAMINE=STEP1_EXAMINE,\
            STEP2_STYLE=STEP2_STYLE,\
            is_logged_in=is_logged_in,\
            is_staff=is_staff,\
            is_superuser=is_superuser)

    if kwargs:
        common_dict.update(kwargs)

    return common_dict
