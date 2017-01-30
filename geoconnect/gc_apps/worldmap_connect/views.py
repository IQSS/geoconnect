from django.http import HttpResponseRedirect, HttpResponse
from django.http import Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from gc_apps.worldmap_connect.models import JoinTargetInformation
from gc_apps.worldmap_connect.send_shapefile_service import SendShapefileService

import logging
logger = logging.getLogger(__name__)


#@login_required
def view_send_shapefile_to_worldmap(request, shp_md5):
    """
    Send shapefile to WorldMap.

    Async the SendShapefileService.send_shapefile_to_worldmap process

    For now, it follows the process and then redirects back to the shapefile page with success (and map) or fail messages
    """
    if not shp_md5:
        raise Http404('No shapefile indicated')

    shp_service = SendShapefileService(**dict(shp_md5=shp_md5))
    shp_service.send_shapefile_to_worldmap()

    if shp_service.has_err:
        # Do something more here!
        print ('-' * 40)
        print ('-- IMPORT TROUBLE --')
        print('\n'.join(shp_service.err_msgs))
        print ('-' * 40)

    return HttpResponseRedirect(reverse('view_shapefile_visualize_attempt', kwargs={'shp_md5': shp_md5 }))

@login_required
def clear_jointarget_info(request):
    """
    For debugging, clear out any JoinTarget Information
    saved from the WorldMap API
    """
    if not request.user.is_superuser:
        return HttpResponse('must be a superuser')

    l = JoinTargetInformation.objects.all()

    cnt = l.count()
    if cnt == 0:
        return HttpResponse('no JoinTargetInformation objects found')

    l.delete()

    return HttpResponse('%s JoinTargetInformation object(s) deleted' % cnt)
