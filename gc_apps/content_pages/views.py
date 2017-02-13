"""View for the home page and other content pages"""

from django.shortcuts import render

def view_home(request):
    """
    Display a list of ShapefileInfo objects, each linked to a detail page.
    For testing, allow the upload of a new shapefile object.
    """
    info_dict = dict(page_title='Geoconnect: Dataverse <--> WorldMap')

    return render(request, 'content_pages/view_home.html', info_dict)
