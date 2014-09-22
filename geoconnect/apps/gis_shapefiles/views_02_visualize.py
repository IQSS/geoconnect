import logging

from django.http import HttpResponseRedirect, HttpResponse, HttpRequest, Http404
from django.views.generic import View
from django.template.loader import render_to_string
from django.template import RequestContext

from apps.gis_shapefiles.models import ShapefileInfo
from apps.worldmap_import.models import WorldMapImportSuccess
from apps.worldmap_import.send_shapefile_service import SendShapefileService

from geo_utils.geoconnect_step_names import GEOCONNECT_STEP_KEY, STEP1_EXAMINE, STEP2_VISUALIZE, STEP3_STYLE

from geo_utils.message_helper_json import MessageHelperJSON
from geo_utils.json_field_reader import JSONFieldReader

from apps.gis_shapefiles.shp_services import get_successful_worldmap_attempt_from_shapefile
logger = logging.getLogger(__name__)

from geo_utils.msg_util import *

def render_visualize_content_div(request, shapefile_info, import_success_object):
    """Render a chunk of HTML that will be passed back in an AJAX response"""

    assert(request, type(HttpRequest))
    assert(shapefile_info, type(ShapefileInfo))
    assert(import_success_object, type(WorldMapImportSuccess))

    d = dict(shapefile_info=shapefile_info\
            , import_success_object=import_success_object)

    return render_to_string('gis_shapefiles/view_03_visualize_layer.html'\
                    , d\
                    , context_instance=RequestContext(request)\
                    )


class ViewAjaxVisualizeShapefile(View):
    """Given the md5 of a ShapefileInfo, attempt to visualize the file on WorldMap

    Return a JSON response
    """
    def generate_json_success_response(self, request, shapefile_info, import_success_object):
        """
        Return JSON message indicating successful visualization

        :param request: HttpRequest
        :param shapefile_info: ShapefileInfo
        :param import_success_object: WorldMapImportSuccess
        :return: { "success" : true
                    , "message" : "Success!"
                    , "data" : { "id_main_panel_content" : " ( map html ) "
                            , "id_main_panel_title" : "Step 2. Visualize Shapefile"
                        }
                }
        """
        assert(request, type(HttpRequest))
        assert(shapefile_info, type(ShapefileInfo))
        assert(import_success_object, type(WorldMapImportSuccess))
        msg('render html')
        visualize_html = render_visualize_content_div(request, shapefile_info, import_success_object)
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

        import_success_object = get_successful_worldmap_attempt_from_shapefile(shapefile_info)
        if import_success_object is not None:
            return self.generate_json_success_response(request, shapefile_info, import_success_object)
            msg('Previous attempt found!!')
            # Previous attempt found!!
            #
            visualize_html = render_visualize_content_div(request, shapefile_info, import_success_object)
            json_msg = MessageHelperJSON.get_json_msg(success=True
                                            , msg='Success!'
                                            , data_dict=dict(id_main_panel_content=visualize_html\
                                                        , id_main_panel_title=STEP2_VISUALIZE\
                                                        )\
                                            )
            return HttpResponse(status=200, content=json_msg, content_type="application/json")

        # (3) Let's visualize this on WorldMap!
        #
        msgt('(3) Let\'s visualize this on WorldMap!')
        send_shp_service = SendShapefileService(**dict(shp_md5=shp_md5))
        send_shp_service.send_shapefile_to_worldmap()

        if send_shp_service.get_import_success_object() is not None:
            msgt('(3a) It worked!')
            return self.generate_json_success_response(request, shapefile_info, import_success_object)

            # (3a) It worked!
            # Send back the results!
            #
            visualize_html = render_visualize_content_div(request, shapefile_info, send_shp_service.import_success_obj)
            json_msg = MessageHelperJSON.get_json_msg(success=True
                                            , msg='Success!'
                                            , data_dict=dict(id_main_panel_content=visualize_html\
                                                             , id_main_panel_title=STEP2_VISUALIZE\
                                                         )\
                                            )
            return HttpResponse(status=200, content=json_msg, content_type="application/json")

        if send_shp_service.has_err:
            msgt('(3a) It worked!')

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


""" logger.debug('Has an import been attempted?')
    latest_import_attempt = WorldMapImportAttempt.get_latest_attempt(shapefile_info)

    if latest_import_attempt:
        logger.debug('latest_import_attempt: %s' % latest_import_attempt )
        import_success_object = latest_import_attempt.get_success_info()
        if import_success_object:
            if just_made_visualize_attempt:
                d['page_title'] = 'Visualize Shapefile'
                d[GEOCONNECT_STEP_KEY] = STEP2_VISUALIZE
            else:
                d['page_title'] = 'Style Shapefile'
                d[GEOCONNECT_STEP_KEY] = STEP3_STYLE

            classify_form = ClassifyLayerForm(**dict(import_success_object=import_success_object))
            #d['form_inline'] = True
            d['classify_form'] = classify_form
            d['ATTRIBUTE_VALUE_DELIMITER'] = ATTRIBUTE_VALUE_DELIMITER

        # (2) run the worldmap import


        # (3) error


        # (4) success
"""
