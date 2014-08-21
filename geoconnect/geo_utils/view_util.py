from django.conf import settings

from geo_utils.geoconnect_step_names import *


def get_common_lookup(request, **kwargs):
    if request is None:
        return {}
    
    if request.user and request.user.is_active and request.user.is_staff:
        is_staff = True
    else:
        is_staff = False

    if request.user and request.user.is_authenticated():
        is_logged_in = True
    else:
        is_logged_in = False
            
    d = dict(DATAVERSE_SERVER_URL=settings.DATAVERSE_SERVER_URL\
            , current_url='%s%s' % (request.get_host(),  request.get_full_path())\
            , DEBUG_MODE=settings.DEBUG\
            , GEOCONNECT_STEPS=GEOCONNECT_STEPS
            , STEP1_EXAMINE=STEP1_EXAMINE
            , STEP2_VISUALIZE=STEP2_VISUALIZE
            , STEP3_STYLE=STEP3_STYLE
            )
    
    return d
