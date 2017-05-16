"""View for the home page and other content pages"""
from django.shortcuts import render
from django.template.loader import render_to_string
from gc_apps.geo_utils.view_util import get_common_lookup
from gc_apps.content_pages.models import MaintenanceMode

def view_home(request):
    """
    Display a list of ShapefileInfo objects, each linked to a detail page.
    For testing, allow the upload of a new shapefile object.
    """
    info_dict = get_common_lookup(request)

    info_dict['page_title'] = 'Geoconnect: Dataverse <--> WorldMap'
    info_dict['maintenance_notice'] = get_maintenance_snippet()

    return render(request, 'content_pages/view_home.html', info_dict)


def get_maintenance_snippet():
    """
    Retrieve a maintenance snippet
    """
    # Is there an active MaintenanceMode object?
    maint_mode = MaintenanceMode.objects.filter(is_active=True).first()

    # Nope!
    if maint_mode is None:
        return None

    # Yes

    # Does it have a message to display directly?
    #
    if maint_mode.message:
        return maint_mode.message

    # Return the maintenance mode template
    #
    maintenance_snippet = render_to_string(\
                            maint_mode.template_name,
                            dict(maint_mode=maint_mode))

    return maintenance_snippet
