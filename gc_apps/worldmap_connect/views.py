"""Convenience method for deleting JoinTargetInformation objects"""

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from gc_apps.worldmap_connect.models import JoinTargetInformation


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

    info_dict = dict(jt_info=JoinTargetInformation.objects.first())

    return render(request, 'show_jointarget_info.html', info_dict)
