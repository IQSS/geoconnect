"""Convenience method for deleting JoinTargetInformation objects"""
import json

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from gc_apps.worldmap_connect.models import JoinTargetInformation
from gc_apps.worldmap_connect.test_quotes import get_random_quote
from gc_apps.geo_utils.view_util import get_common_lookup

import logging

LOGGER = logging.getLogger(__name__)

@login_required
def view_test_err_log(request):
    """To debug the log handling--e.g. ".error" events should be emailed"""

    movie_quote = get_random_quote()
    #print '%s, %s' % (__name__, LOGGER)
    LOGGER.error(movie_quote)

    return HttpResponse(movie_quote)


@login_required
def clear_jointarget_info(request):
    """
    For debugging, clear out any JoinTarget Information
    saved from the WorldMap API
    """
    if not request.user.is_superuser:
        return HttpResponse('must be a superuser')

    jtarget_list = JoinTargetInformation.objects.all()

    cnt = jtarget_list.count()
    if cnt == 0:
        return HttpResponse('no JoinTargetInformation objects found')

    jtarget_list.delete()

    return HttpResponse('%s JoinTargetInformation object(s) deleted' % cnt)


def show_jointarget_info(request):
    """Display the latest Join Targets retrieved from the WorldMap"""

    target_info_list = None
    target_info_pretty = None

    jt_info = JoinTargetInformation.objects.first()
    if jt_info:
        target_info_list_unsorted = jt_info.target_info.get('data')

        # sort the info by type
        target_info_list = sorted(\
                        target_info_list_unsorted,
                        key=lambda k: k['geocode_type'])

        target_info_pretty = json.dumps(target_info_list, indent=4)

    info_dict = get_common_lookup(request)
    info_dict['target_info_list'] = target_info_list
    info_dict['target_info_pretty'] = target_info_pretty

    return render(request, 'show_jointarget_info.html', info_dict)
