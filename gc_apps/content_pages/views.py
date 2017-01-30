import logging

from django.shortcuts import render

from django.http import HttpResponseRedirect, HttpResponse, Http404

def view_home(request):
    """
    Display a list of :model:`gis_shapefiles.ShapefileInfo` objects, each linked to a detail page.
    For testing, allow the upload of a new shapefile object.
    """
    d = { 'page_title' : 'Shapefiles: Test Upload Page'\
        }


    return render(request, 'content_pages/view_home.html', d)

#def view_content_not_accepted(request)
