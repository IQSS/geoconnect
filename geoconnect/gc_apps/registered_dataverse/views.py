from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render

from gc_apps.registered_dataverse.models import IncomingFileTypeSetting


def view_filetype_note_by_name(request, file_type_name):
    try:
        ftype_setting = IncomingFileTypeSetting.objects.get(name=file_type_name)
    except IncomingFileTypeSetting.DoesNotExist:
        raise Http404('IncomingFileTypeSetting not found for: %s' %\
                file_type_name)

    d = dict(ftype_setting=ftype_setting)

    return render(request, 'registered_dataverse/view_filetype_note.html', d)

def view_filetype_note(request, file_type_slug):

    try:
        ftype_setting = IncomingFileTypeSetting.objects.get(slug=file_type_slug)
    except IncomingFileTypeSetting.DoesNotExist:
        raise Http404('IncomingFileTypeSetting not found for: %s' %\
                file_type_slug)

    d = dict(ftype_setting=ftype_setting)

    return render(request, 'registered_dataverse/view_filetype_note.html', d)

def view_filetype_list(request):

    ftype_list = IncomingFileTypeSetting.objects.all()

    d = dict(ftype_list=ftype_list)

    return render(request, 'registered_dataverse/view_filetype_list.html', d)
