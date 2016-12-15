"""
Help with assembling HTML snippets for AJAX calls that:
 - update the breadcrumb
 - update the title
"""

from django.template.loader import render_to_string
from geo_utils.geoconnect_step_names import GEOCONNECT_STEP_KEY,\
    GEOCONNECT_STEPS, STEP2_STYLE # STEP1_EXAMINE

# Create your views here.
def render_breadcrumb_div_for_style_step():
    """
    Create HTML snippet for breadcrumb
    """
    template_dict = {GEOCONNECT_STEP_KEY : STEP2_STYLE,\
        'GEOCONNECT_STEPS' : GEOCONNECT_STEPS}

    return render_to_string('breadcrumb.html', template_dict)

def render_main_panel_title_for_style_step(gis_data_info):
    """
    Create HTML snippet for title of Main Panel
    """
    assert hasattr(gis_data_info, 'datafile_label'), "shapefile_info must be a ShapefileInfo object"

    template_dict = {'gis_data_info' : gis_data_info,\
                    GEOCONNECT_STEP_KEY : STEP2_STYLE}
    return render_to_string('gis_shapefiles/view_02_main_panel_title.html',\
        template_dict)
