"""
Views for classifying a layer
"""
from __future__ import print_function
import requests
import logging

from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import render_to_string

from django.conf import settings

from geo_utils.message_helper_json import MessageHelperJSON
#from geo_utils.msg_util import msg
from apps.dv_notify.metadata_updater import MetadataUpdater
from apps.classification.utils import get_worldmap_info_object
from apps.gis_tabular.forms import SELECT_LABEL
from geo_utils.json_field_reader import JSONHelper

from shared_dataverse_information.layer_classification.forms import\
    ClassifyLayerForm, ATTRIBUTE_VALUE_DELIMITER
from shared_dataverse_information.layer_classification.forms_api import\
    ClassifyRequestDataForm
from shared_dataverse_information.map_layer_metadata.forms import\
    WorldMapToGeoconnectMapLayerMetadataValidationForm


LOGGER = logging.getLogger(__name__)


def format_major_error_message(err_msg, import_success_md5=None):
    """
    This error is severe and replaces the entire classify form
    """
    params = dict(error_message=err_msg,\
                import_success_md5=import_success_md5)
    return render_to_string('classification/classify_major_error.html', params)

def format_minor_error_message(err_msg):
    return render_to_string('classification/classify_basic_error.html',\
        dict(error_message=err_msg))

#@login_required
def view_classify_layer_form(request, import_success_md5):
    """
    Given a ClassifyLayerForm submission, return a JSON response

    :param import_success_md5: str, md5 identifying a WorldMapLayerInfo object
    :returns JSON response: JSON generated with the MessageHelperJSON.get_json_msg function
    """
    # --------------------------------------------------------------
    # Is it a POST?
    # --------------------------------------------------------------
    if not request.POST:
        err_note = 'A POST request must be used to classify the layer.'

        div_content = format_major_error_message(err_note,\
            import_success_md5=import_success_md5)
        json_msg = MessageHelperJSON.get_json_msg(success=False,\
                        msg=err_note,\
                        data_dict=dict(div_content=div_content))
        # technically a 405 error, but we want the JSON message to appear
        return HttpResponse(status=200,\
                        content=json_msg,\
                        content_type="application/json")

    # --------------------------------------------------------------
    # Is the WorldMapLayerInfo object md5 available?
    # --------------------------------------------------------------
    if not import_success_md5:
        err_note = 'Sorry! The layer could not be identified.\n\nThe Styling option is not available.'
        json_msg = MessageHelperJSON.get_json_msg(success=False\
                                                , msg=err_note\
                                                , data_dict=dict(div_content=format_major_error_message(err_note)))
        # technically a 404 error, but we want the JSON message to appear
        return HttpResponse(status=200, content=json_msg, content_type="application/json")

    # --------------------------------------------------------------
    # Does the WorldMapLayerInfo object exist?
    # --------------------------------------------------------------
    if not 'data_source_type' in request.POST:
        err_note = 'Sorry! The layer could not be identified.\n\nThe Styling option is not available. (id:ds2)'
        json_msg = MessageHelperJSON.get_json_msg(success=False\
                                            , msg=err_note\
                                            , data_dict=dict(div_content=format_major_error_message(err_note)))
        return HttpResponse(status=200, content=json_msg, content_type="application/json")

    # Retrieve an object containing the WorldMap data
    #
    worldmap_layerinfo = get_worldmap_info_object(request.POST['data_source_type'],\
                                import_success_md5)

    if worldmap_layerinfo is None:
        err_note = 'Sorry! The layer data could not be found.\n\nThe Styling option is not available. (id:ds3)'
        json_msg = MessageHelperJSON.get_json_msg(success=False\
                                                , msg=err_note\
                                                , data_dict=dict(div_content=format_major_error_message(err_note)))
        # technically a 410 error, but we want the JSON message to appear
        return HttpResponse(status=200, content=json_msg, content_type="application/json")


    d = { 'ATTRIBUTE_VALUE_DELIMITER' :ATTRIBUTE_VALUE_DELIMITER }

    # --------------------------------------------------------------
    # Is the form valid?
    # --------------------------------------------------------------

    # Load up classification form parameters and validate this request
    #   e.g. Is the classification attribute in the AJAX call actually
    #       part of this layer? etc.
    #
    classify_form = ClassifyLayerForm(request.POST, **worldmap_layerinfo.get_dict_for_classify_form())

    # --------------------------------------------------------------
    # Invalid forms are status=200 so caught by ajax
    # Form validation will replace the classification div on the page
    # --------------------------------------------------------------
    if not classify_form.is_valid():    # Oops, not valid (shouldn't happen)
        user_message = ('There was an error with the styling form.'
                        ' Please check the errors below.')
        d.update( dict(classify_form=classify_form,
                  worldmap_layerinfo=worldmap_layerinfo,
                  error_msg=user_message,
                ))
        form_content = render_to_string('classification/view_classify_form.html', d\
                                , context_instance=RequestContext(request))
        json_msg = MessageHelperJSON.get_json_msg(success=False
                                            , msg=user_message
                                            , data_dict={'div_content':form_content}\
                                            )
        return HttpResponse(status=200, content=json_msg, content_type="application/json")

    initial_classify_params = classify_form.get_params_dict_for_classification()
    if initial_classify_params is None:
        LOGGER.error('Failed with *valid* form: classify_form.get_params_dict_for_classification()')
        json_msg = MessageHelperJSON.get_json_msg(success=False,\
            msg='The layer styling form contains errors (code: 2)')
        return HttpResponse(status=200, content=json_msg, content_type="application/json")

    #----------------------------------------------------------
    # Prepare params for classify request against WorldMap API
    #
    #----------------------------------------------------------
    check_for_existing_layer_params = worldmap_layerinfo.get_params_to_check_for_existing_layer_metadata()
    initial_classify_params.update(check_for_existing_layer_params)

    api_form = ClassifyRequestDataForm(initial_classify_params)
    if not api_form.is_valid():
        LOGGER.error(('Validation failed with ClassifyRequestDataForm. '
                    'Errors: %s', api_form.errors))
        json_msg = MessageHelperJSON.get_json_msg(success=False, msg='The layer styling form contains errors (code: 3)')
        return HttpResponse(status=200, content=json_msg, content_type="application/json")


    classify_params = api_form.cleaned_data

    classify_url = classify_form.get_worldmap_classify_api_url()
    #print ('classify_params', classify_params)
    resp = None
    try:
        resp = requests.post(classify_url,\
                    data=classify_params,\
                    auth=settings.WORLDMAP_ACCOUNT_AUTH,\
                    timeout=settings.WORLDMAP_DEFAULT_TIMEOUT)
    except requests.exceptions.ConnectionError as e:
        err_msg = '<p><b>Details for administrator:</b> Could not contact the Dataverse server: %s</p><p>%s</p>'\
                                % (classify_url, e.message)
        LOGGER.error(err_msg)
        json_msg = MessageHelperJSON.get_json_msg(success=False, msg='Sorry!  The classification failed.<br />%s' % err_msg)
        return HttpResponse(status=200, content=json_msg, content_type="application/json")

    if not resp.status_code == 200:
        try:
            json_resp = resp.json()
        except:
            error_msg = ('Worldmap classification failed. Status code:'
                        ' %s\nText;%s',
                            (resp.status_code, resp.text.encode('utf-8')))
            LOGGER.error(error_msg)
            json_msg = MessageHelperJSON.get_json_msg(success=False,\
                msg='Sorry!  The classification failed.')
            return HttpResponse(status=200, content=json_msg, content_type="application/json")

        wm_err_msg = json_resp.get('message', None)
        if wm_err_msg is None:
            wm_err_msg = 'No message given.'

        err_msg = 'Sorry!  The classification failed.<p>(%s)</p>' % wm_err_msg

        json_msg = MessageHelperJSON.get_json_msg(success=False, msg=err_msg)

        return HttpResponse(status=200, content=json_msg, content_type="application/json")


    # RESPONSE CODE IS 200

    # --------------------------------------------------------------
    # convert response to JSON
    # --------------------------------------------------------------
    try:
        json_resp = resp.json()
    except:
        LOGGER.error('Worldmap response was not valid json: %s',\
                resp.text.encode('utf-8'))
        json_msg = MessageHelperJSON.get_json_msg(success=False,\
            msg='Sorry!  The classification failed.')
        return HttpResponse(status=200,\
            content=json_msg,\
            content_type="application/json")

    # --------------------------------------------------------------
    #   Classification Failed
    # --------------------------------------------------------------
    if not json_resp.get("success") is True:
        LOGGER.error('Worldmap response did not have success==true: %s', resp.text)
        user_msg = 'Sorry!  The classification failed.<br /><br />(%s)', json_resp.get('message', 'nada')
        json_msg = MessageHelperJSON.get_json_msg(success=False, msg=user_msg)
        return HttpResponse(status=200, content=json_msg, content_type="application/json")

    # --------------------------------------------------------------
    #   Validate the response
    # --------------------------------------------------------------
    f_val = WorldMapToGeoconnectMapLayerMetadataValidationForm(json_resp.get('data', None))
    if not f_val.is_valid():
        LOGGER.error('Classify return data failed validation: %s', f_val.errors)
        user_msg = 'Sorry!  The classification failed.<br /><br />(%s)' \
                        % json_resp.get('message', f_val.errors)
        json_msg = MessageHelperJSON.get_json_msg(success=False, msg=user_msg)
        return HttpResponse(status=200, content=json_msg, content_type="application/json")

    # --------------------------------------------------------------
    #   Looks good, update the WorldMapLayerInfo's attribute info
    # --------------------------------------------------------------
    if hasattr(worldmap_layerinfo, 'add_attribute_info_as_json_string'):
        # handle shapefiles
        worldmap_layerinfo.add_attribute_info_as_json_string(f_val.cleaned_data['attribute_info'])
        worldmap_layerinfo.save()
    elif hasattr(worldmap_layerinfo, 'attribute_data'):
        # handle tabular files
        worldmap_layerinfo.attribute_info = JSONHelper.to_python_or_none(f_val.cleaned_data['attribute_info'])
        worldmap_layerinfo.download_links = JSONHelper.to_python_or_none(f_val.cleaned_data['download_links'])
        worldmap_layerinfo.save()
    else:
        print (dir(worldmap_layerinfo))
        print (type(worldmap_layerinfo))
        print ('nada?')

    # --------------------------------------------------------------
    # Refresh the classify form with the latest WorldMap parameter information
    # --------------------------------------------------------------
    classify_form = ClassifyLayerForm(request.POST, **worldmap_layerinfo.get_dict_for_classify_form())

    # --------------------------------------------------------------
    # Update the Dataverse metadata -- so that the new icon will be refreshed
    # --------------------------------------------------------------

    # Is all this needed, or should there be a
    # Dataverse API call to only update the image?
    MetadataUpdater.update_dataverse_with_metadata(worldmap_layerinfo)

    msg_params = classify_form.get_params_for_display()

    success_msg =  render_to_string('classification/classify_success_msg.html', msg_params)
    d.update(dict(classify_form=classify_form,
             success_msg=success_msg,
             SELECT_LABEL=SELECT_LABEL,
            ))

    form_content = render_to_string('classification/view_classify_form.html', d\
                            , context_instance=RequestContext(request))


    json_msg = MessageHelperJSON.get_json_msg(success=True,
                                            msg=success_msg, #'Success!'
                                            data_dict={'div_content':form_content}\
                                        )
    return HttpResponse(status=200, content=json_msg, content_type="application/json")
