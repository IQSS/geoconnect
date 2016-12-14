import logging

from django.http import HttpResponse
from django.views.generic import View
from django.template.loader import render_to_string
from django.template import RequestContext

from django.conf import settings

from apps.gis_shapefiles.models import ShapefileInfo
from apps.worldmap_layers.models import WorldMapLayerInfo

from apps.worldmap_connect.send_shapefile_service import SendShapefileService

from geo_utils.geoconnect_step_names import GEOCONNECT_STEP_KEY, STEP2_STYLE

from shared_dataverse_information.layer_classification.forms import\
    ClassifyLayerForm, ATTRIBUTE_VALUE_DELIMITER

from geo_utils.message_helper_json import MessageHelperJSON
from apps.gis_tabular.views import build_map_html

from apps.gis_basic_file.views import render_breadcrumb_div_for_style_step,\
    render_main_panel_title_for_style_step

LOGGER = logging.getLogger(__name__)


from geo_utils.msg_util import msg, msgt


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


def render_visualize_content_div(request, shapefile_info, worldmap_layerinfo):
    """Render a chunk of HTML that will be passed back in an AJAX response"""

    #assert False, "This should be similar to views.view_classify_shapefile!!!"


    assert type(shapefile_info) is ShapefileInfo, "shapefile_info must be a ShapefileInfo object"
    assert isinstance(worldmap_layerinfo, WorldMapLayerInfo),\
        "worldmap_layerinfo must be a WorldMapLayerInfo object"



    classify_form = ClassifyLayerForm(**worldmap_layerinfo.get_dict_for_classify_form())


    d = dict(shapefile_info=shapefile_info\
            , worldmap_layerinfo=worldmap_layerinfo\
            , core_data=worldmap_layerinfo.core_data\
            , download_links=worldmap_layerinfo.download_links\
            , attribute_data=worldmap_layerinfo.attribute_data\
            , classify_form=classify_form\
            , delete_form=delete_form\
            , ATTRIBUTE_VALUE_DELIMITER=ATTRIBUTE_VALUE_DELIMITER\
            , show_visualize_success_msg=True\
        )


    d[GEOCONNECT_STEP_KEY] = STEP2_STYLE    # Used to display delete button

    #d['classify_form'] = classify_form
    #d['ATTRIBUTE_VALUE_DELIMITER'] = ATTRIBUTE_VALUE_DELIMITER
    return render_to_string('gis_tabular/view_tabular_map_div.html',\
                        d,\
                        context_instance=RequestContext(request))
    #return render_to_string('gis_shapefiles/view_04_ajax_style_layer.html'\
    #                , d\
    #                , context_instance=RequestContext(request)\
    #                )

    # -----------------------------
    # Without classify form:
    # -----------------------------
    #d = dict(shapefile_info=shapefile_info\
    #        , worldmap_layerinfo=worldmap_layerinfo\
    #    )
    #return render_to_string('gis_shapefiles/view_03_visualize_layer.html'\


class ViewAjaxVisualizeShapefile(View):
    """
    Given the md5 of a ShapefileInfo, attempt to visualize the file on WorldMap

    Return a JSON response
    """
    def generate_json_success_response(self, request, shapefile_info, worldmap_layerinfo):
        """
        Return JSON message indicating successful visualization

        :param request: HttpRequest
        :param shapefile_info: ShapefileInfo
        :param worldmap_layerinfo: WorldMapLayerInfo
        :return: { "success" : true
                    , "message" : "Success!"
                    , "data" : { "id_main_panel_content" : " ( map html ) "
                            , "id_main_panel_title" : "( title panel html)"
                            , "id_breadcrumb" : "(breadcrumb html)"
                        }
                }
        """
        #assert type(request) is HttpRequest, "request must be a HttpRequest object"
        assert isinstance(shapefile_info, ShapefileInfo), "shapefile_info must be a ShapefileInfo object"
        assert isinstance(worldmap_layerinfo, WorldMapLayerInfo), "worldmap_layerinfo must be a WorldMapLayerInfo object"

        msg('render html')
        visualize_html = render_visualize_content_div(request, shapefile_info, worldmap_layerinfo)
        breadcrumb_html = render_breadcrumb_div_for_style_step()
        main_title_panel_html = render_main_panel_title_for_style_step(shapefile_info)

        msg('create  json_msg')
        json_msg = MessageHelperJSON.get_json_msg(success=True
                        , msg='Success!'\
                        , data_dict=dict(id_main_panel_content=visualize_html\
                                    , id_main_panel_title=main_title_panel_html\
                                    , id_breadcrumb=breadcrumb_html
                                        )\
                        )
        msg('send  json_msg')
        return HttpResponse(status=200, content=json_msg, content_type="application/json")


    def get(self, request, shp_md5):

        # (3) Let's visualize this on WorldMap!
        #
        LOGGER.debug('(3) Let\'s visualize this on WorldMap!')

        send_shp_service = SendShapefileService(**dict(shp_md5=shp_md5))

        LOGGER.debug('(3a) send_shapefile_to_worldmap')
        success = send_shp_service.send_shapefile_to_worldmap()

        # -----------------------------------
        # Did shapefile create work?
        # -----------------------------------


        # NOPE!  Failed along the way!
        # -----------------------------------
        if not success:

            msg(send_shp_service.err_msgs)

            err_note = "Sorry! The shapefile mapping did not work.<br /><span class='small'>%s</span>" % '<br />'.join(send_shp_service.err_msgs)

            err_note_html = render_ajax_basic_err_msg(err_note,\
                                            send_shp_service.shapefile_info)

            json_msg = MessageHelperJSON.get_json_msg(success=False,\
                        msg=err_note,\
                        data_dict=dict(id_main_panel_content=err_note_html)
                    )

            return HttpResponse(status=200, content=json_msg, content_type="application/json")

        # Yes!  We have a new map layer -
        # -----------------------------------
        worldmap_shapefile_layerinfo = send_shp_service.get_worldmap_layerinfo()
        shapefile_info = worldmap_shapefile_layerinfo.get_gis_data_info()


        assert worldmap_shapefile_layerinfo is not None,\
            "Failure in SendShapefileService!  Said success but not worldmap_layerinfo (WorldMapShapefileLayerInfo)"

        # ^^^^^^^^^
        # -----------------------------------------
        # Build the Map HTML chunk to replace the form
        # -----------------------------------------
        map_html = build_map_html(request, worldmap_shapefile_layerinfo)
        if map_html is None:    # Failed!  Send an error
            LOGGER.error("Failed to create map HTML using WorldMapShapefileLayerInfo: %s (%d)",\
                worldmap_shapefile_layerinfo, worldmap_shapefile_layerinfo.id)
            user_msg = 'Sorry! Failed to create map. Please try again. (code: s3)'
            json_msg = MessageHelperJSON.get_json_fail_msg(user_msg)
            return HttpResponse(json_msg, mimetype="application/json", status=200)

        # -----------------------------------------
        # Looks good.  In the JSON response, send
        #   back the map HTML
        # -----------------------------------------
        main_title_panel_html=render_main_panel_title_for_style_step(shapefile_info)
        data_dict = dict(map_html=map_html,\
                    id_breadcrumb=render_breadcrumb_div_for_style_step(),\
                    id_main_panel_title=main_title_panel_html)

        json_msg = MessageHelperJSON.get_json_success_msg("great job", data_dict=data_dict)

        return HttpResponse(json_msg, mimetype="application/json", status=200)

        #return self.generate_json_success_response(request, shapefile_info, worldmap_layerinfo)
