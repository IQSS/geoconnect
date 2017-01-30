import logging

from django.http import HttpResponse
from django.views.generic import View
from django.template.loader import render_to_string

from django.conf import settings

from gc_apps.gis_shapefiles.models import ShapefileInfo
from gc_apps.worldmap_layers.models import WorldMapLayerInfo

from gc_apps.worldmap_connect.send_shapefile_service import SendShapefileService

from gc_apps.geo_utils.geoconnect_step_names import GEOCONNECT_STEP_KEY, STEP2_STYLE,\
    PANEL_TITLE_MAP_DATA_FILE, PANEL_TITLE_STYLE_MAP

from shared_dataverse_information.layer_classification.forms import\
    ClassifyLayerForm, ATTRIBUTE_VALUE_DELIMITER

from gc_apps.geo_utils.message_helper_json import MessageHelperJSON
from gc_apps.gis_tabular.views import build_map_html

LOGGER = logging.getLogger(__name__)


from gc_apps.geo_utils.msg_util import msg, msgt


"""
Handle AJAX requests to Visualize a Layer

- Upon successful visualizations, several pieces of the page are update including
    - page title
    - breadcrumb
    - main content panel
"""


def render_ajax_basic_err_msg(err_note, shapefile_info=None):
    """Convenience method for returning an error message via AJAX"""

    d = {   'DATAVERSE_SERVER_URL' : settings.DATAVERSE_SERVER_URL\
            , 'ERR_NOTE' : err_note\
            , 'shapefile_info' : shapefile_info\
         }
    return render_to_string('gis_shapefiles/view_02_ajax_basic_err.html', d)



class ViewAjaxVisualizeShapefile(View):
    """
    Given the md5 of a ShapefileInfo, attempt to visualize the file on WorldMap

    Return a JSON response
    """
    def get(self, request, shp_md5):
        """Use the SendShapefileService to create a map from a shapefile.

        - SendShapefileService takes care of details starting with retrieving
        the ShapefileInfo object
        """

        # OK if shp_md5 is None, SendShapefileService creates error message
        #
        send_shp_service = SendShapefileService(**dict(shp_md5=shp_md5))

        # Send the shapefile to WorldMap
        #
        success = send_shp_service.send_shapefile_to_worldmap()

        # -----------------------------------
        # Did it work? NOPE!  Failed along the way!
        # -----------------------------------
        if not success:
            err_note = "Sorry! The shapefile mapping did not work.<br /><span class='small'>%s</span>" % '<br />'.join(send_shp_service.err_msgs)
            LOGGER.error(err_note)
            err_note_html = render_ajax_basic_err_msg(err_note,\
                                            send_shp_service.shapefile_info)

            json_msg = MessageHelperJSON.get_json_fail_msg(err_note_html, dict(id_main_panel_content=err_note_html))

            return HttpResponse(json_msg, content_type="application/json", status=200)


        # -----------------------------------
        # Yes!  We have a new map layer
        # -----------------------------------
        worldmap_shapefile_layerinfo = send_shp_service.get_worldmap_layerinfo()
        shapefile_info = worldmap_shapefile_layerinfo.get_gis_data_info()

        assert worldmap_shapefile_layerinfo is not None,\
            "Failure in SendShapefileService!  Said success but not worldmap_layerinfo (WorldMapShapefileLayerInfo)"

        # -----------------------------------------
        # Build the Map HTML to replace the form
        # -----------------------------------------
        map_html, user_message_html = build_map_html(request, worldmap_shapefile_layerinfo)
        if map_html is None:    # Failed!  Send an error
            LOGGER.error("Failed to create map HTML using WorldMapShapefileLayerInfo: %s (%d)",\
                worldmap_shapefile_layerinfo, worldmap_shapefile_layerinfo.id)

            user_msg = 'Sorry! Failed to create map. Please try again. (code: s3)'
            json_msg = MessageHelperJSON.get_json_fail_msg(user_msg)
            return HttpResponse(json_msg, content_type="application/json", status=200)

        # -----------------------------------------
        # Looks good.  In the JSON response, send
        #   back the map HTML
        # -----------------------------------------
        data_dict = dict(map_html=map_html,
                    user_message_html=user_message_html,
                    id_main_panel_title=PANEL_TITLE_STYLE_MAP,
                    message='Success!  The shapefile was successfully mapped!')

        json_msg = MessageHelperJSON.get_json_success_msg("great job", data_dict=data_dict)

        return HttpResponse(json_msg, content_type="application/json", status=200)
