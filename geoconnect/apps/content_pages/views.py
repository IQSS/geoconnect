import logging

from django.shortcuts import render_to_response

from django.http import HttpResponseRedirect, HttpResponse, Http404

from django.template import RequestContext


def view_home(request):
    """
    Display a list of :model:`gis_shapefiles.ShapefileInfo` objects, each linked to a detail page.
    For testing, allow the upload of a new shapefile object.

    **Context**

    ``RequestContext``

    :ShapefileInfoForm: Check for a ShapefileInfoForm object in the request.POST

    **Template:**

    :template:`gis_shapefiles/view_01_examine_zip.html`
    """
    d = { 'page_title' : 'Shapefiles: Test Upload Page'\
        }


    return render_to_response('content_pages/view_home.html'\
                            , d
                            , context_instance=RequestContext(request))
