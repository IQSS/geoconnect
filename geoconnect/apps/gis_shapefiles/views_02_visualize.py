import logging

from django.http import HttpResponseRedirect, HttpResponse, HttpRequest, Http404
from django.views.generic import View
from django.template.loader import render_to_string
from django.template import RequestContext

from apps.gis_shapefiles.models import ShapefileInfo
from apps.worldmap_connect.models import WorldMapLayerInfo
from apps.worldmap_connect.send_shapefile_service import SendShapefileService

from geo_utils.geoconnect_step_names import GEOCONNECT_STEP_KEY, STEP1_EXAMINE, STEP2_VISUALIZE, STEP3_STYLE

from geo_utils.message_helper_json import MessageHelperJSON
#from geo_utils.json_field_reader import JSONFieldReader

from apps.gis_shapefiles.shp_services import get_successful_worldmap_attempt_from_shapefile

logger = logging.getLogger(__name__)

from geo_utils.msg_util import *

def render_visualize_content_div(request, shapefile_info, worldmap_layerinfo):
    """Render a chunk of HTML that will be passed back in an AJAX response"""

    assert(request, type(HttpRequest))
    assert(shapefile_info, type(ShapefileInfo))
    assert(worldmap_layerinfo, type(WorldMapLayerInfo))

    d = dict(shapefile_info=shapefile_info\
            , worldmap_layerinfo=worldmap_layerinfo\
        )


    return render_to_string('gis_shapefiles/view_03_visualize_layer.html'\
                    , d\
                    , context_instance=RequestContext(request)\
                    )


class ViewAjaxVisualizeShapefile(View):
    """Given the md5 of a ShapefileInfo, attempt to visualize the file on WorldMap

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
                            , "id_main_panel_title" : "Step 2. Visualize Shapefile"
                        }
                }
        """
        assert(request, type(HttpRequest))
        assert(shapefile_info, type(ShapefileInfo))
        assert(worldmap_layerinfo, type(WorldMapLayerInfo))
        msg('render html')
        visualize_html = render_visualize_content_div(request, shapefile_info, worldmap_layerinfo)
        msg('create  json_msg')
        json_msg = MessageHelperJSON.get_json_msg(success=True
                                        , msg='Success!'
                                        , data_dict=dict(id_main_panel_content=visualize_html\
                                                    , id_main_panel_title=STEP2_VISUALIZE\
                                                    )\
                                        )
        msg('send  json_msg')
        return HttpResponse(status=200, content=json_msg, content_type="application/json")


    def get(self, request, shp_md5):

        d = {}

        # (1) Retrieve the ShapefileInfo object
        #
        msgt('Retrieve the ShapefileInfo object')
        try:
            shapefile_info = ShapefileInfo.objects.get(md5=shp_md5)
        except ShapefileInfo.DoesNotExist:
            err_note = "Sorry!  The shapefile was not found.  Please return to the Dataverse."
            json_msg = MessageHelperJSON.get_json_msg(success=False\
                                 , msg=err_note\
                                 , data_dict=dict(id_main_panel_content=err_note)
            )
            logger.error('Shapefile not found for hash: %s' % shp_md5)
            return HttpResponse(status=200, content=json_msg, content_type="application/json")


        # (2) Check for a previous, successful visualization attempt
        #   If one exists, send it over!
        #
        # UPDATE: use WorldMap API to check user and shapefile id
        #
        msgt('(2) Check for a previous, successful visualization attempt')

        worldmap_layerinfo = get_successful_worldmap_attempt_from_shapefile(shapefile_info)
        if worldmap_layerinfo is not None:
            # (2a) Previous attempt found!!
            msg('Previous attempt found!!')
            return self.generate_json_success_response(request, shapefile_info, worldmap_layerinfo)


        # (3) Let's visualize this on WorldMap!
        #
        msgt('(3) Let\'s visualize this on WorldMap!')

        send_shp_service = SendShapefileService(**dict(shp_md5=shp_md5))

        send_shp_service.send_shapefile_to_worldmap()

        worldmap_layerinfo = send_shp_service.get_worldmap_layerinfo()

        if worldmap_layerinfo is not None:
            return self.generate_json_success_response(request, shapefile_info, worldmap_layerinfo)

        
        if send_shp_service.has_err:
            msgt('(3a) It didn\'t worked!')
            msg(send_shp_service.err_msgs)
            # (3b) Uh oh!  Failed to visualize
            #
            err_note = "Sorry!  The shapefile mapping did not work.  Please return to the Dataverse. <br />%s" % '<br />'.join(send_shp_service.err_msgs)
            json_msg = MessageHelperJSON.get_json_msg(success=False\
                                 , msg=err_note\
                                 , data_dict=dict(id_main_panel_content=err_note)
            )
            return HttpResponse(status=200, content=json_msg, content_type="application/json")


        # (4) Unanticipated error
        msgt('(4) Unanticipated error')
        err_note = "Sorry!  An error occurred.  A message was sent to the administrator."
        json_msg = MessageHelperJSON.get_json_msg(success=False\
                                 , msg=err_note\
                                 , data_dict=dict(id_main_panel_content=err_note)
            )

        return HttpResponse(status=200, content=json_msg, content_type="application/json")

