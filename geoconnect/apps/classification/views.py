from __future__ import print_function
import requests
import logging

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from geo_utils.message_helper_json import MessageHelperJSON

from apps.dv_notify.metadata_updater import MetadataUpdater
from apps.worldmap_connect.models import WorldMapImportAttempt, WorldMapImportFail, WorldMapLayerInfo
from apps.classification.forms import ClassifyLayerForm, ATTRIBUTE_VALUE_DELIMITER

from shared_dataverse_information.map_layer_metadata.forms import WorldMapToGeoconnectMapLayerMetadataValidationForm


logger = logging.getLogger(__name__)


def format_major_error_message(msg, import_success_md5=None):
    """
    This error is severe and replaces the entire classify form
    """
    return render_to_string('classification/classify_major_error.html', dict(error_message=msg,import_success_md5=import_success_md5))

def format_minor_error_message(msg):
    return render_to_string('classification/classify_basic_error.html', dict(error_message=msg))

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
        json_msg = MessageHelperJSON.get_json_msg(success=False\
                                  , msg=err_note\
                                 , data_dict=dict(div_content=format_major_error_message(err_note, import_success_md5=import_success_md5)))
        # technically a 405 error, but we want the JSON message to appear
        return HttpResponse(status=200, content=json_msg, content_type="application/json")
    
    # --------------------------------------------------------------
    # Is the WorldMapLayerInfo object md5 available?
    # --------------------------------------------------------------
    if not import_success_md5:
        err_note = 'Sorry! The layer could not be identified.\n\nThe Styling option is not available.'
        json_msg = MessageHelperJSON.get_json_msg(success=False\
                                                , msg=err_note\
                                                , data_dict=dict(div_content=format_major_error_message(err_note)))
        # technically a 400 error, but we want the JSON message to appear
        return HttpResponse(status=200, content=json_msg, content_type="application/json")
         
    # --------------------------------------------------------------
    # Does the success object exist?
    # --------------------------------------------------------------
    try: 
        worldmap_layerinfo = WorldMapLayerInfo.objects.get(md5=import_success_md5)
    except WorldMapLayerInfo.DoesNotExist:
        err_note = 'Sorry! The layer data could not be found.\n\nThe Styling option is not available. (WorldMapLayerInfo object not found)'
        json_msg = MessageHelperJSON.get_json_msg(success=False\
                                                , msg=err_note\
                                                , data_dict=dict(div_content=format_major_error_message(err_note)))
        # technically a 410 error, but we want the JSON message to appear
        return HttpResponse(status=200, content=json_msg, content_type="application/json")
        

    d = { 'ATTRIBUTE_VALUE_DELIMITER' :ATTRIBUTE_VALUE_DELIMITER }
    
    # --------------------------------------------------------------
    # Is the form valid?
    # --------------------------------------------------------------
    classify_form = ClassifyLayerForm(request.POST, **dict(worldmap_layerinfo=worldmap_layerinfo))

    # --------------------------------------------------------------
    # Invalid forms are status=200 so caught by ajax
    # Form validation will replace the classification div on the page
    # --------------------------------------------------------------
    if not classify_form.is_valid():
        d.update( dict(classify_form=classify_form\
                , worldmap_layerinfo=worldmap_layerinfo\
                , error_msg='The form submission contains errors'\
                ))
        form_content = render_to_string('classification/view_classify_form.html', d\
                                , context_instance=RequestContext(request))
        json_msg = MessageHelperJSON.get_json_msg(success=False
                                            , msg='The form submission contains errors'
                                            , data_dict={'div_content':form_content}\
                                            )    
                                                    
        return HttpResponse(status=200, content=json_msg, content_type="application/json")

    classify_params = classify_form.get_params_dict_for_classification()
    if classify_params is None:
        logger.error('Failed with valid form: classify_form.get_params_dict_for_classification()')
        json_msg = MessageHelperJSON.get_json_msg(success=False, msg='The layer styling form contains errors (code: 2)')            
        return HttpResponse(status=200, content=json_msg, content_type="application/json")

    classify_url = classify_form.get_worldmap_classify_api_url()


    resp = None
    try:
        resp = requests.post(classify_url, data=classify_params, timeout=2)
        print ('classify_params', classify_params)
    except requests.exceptions.ConnectionError as e:
        err_msg = '<p><b>Details for administrator:</b> Could not contact the Dataverse server: %s</p><p>%s</p>'\
                                % (classify_url, e.message)
        logger.error(err_msg)
        json_msg = MessageHelperJSON.get_json_msg(success=False, msg='Sorry!  The classification failed.<br />%s' % err_msg)
        return HttpResponse(status=200, content=json_msg, content_type="application/json")


    if resp.status_code == 200:
        #json_resp = resp.json()

        # --------------------------------------------------------------
        # convert response to JSON
        # --------------------------------------------------------------        
        try:
            json_resp = resp.json()
        except:
            logger.error('Worldmap call did not parse into valid json: %s' % json.text)
            json_msg = MessageHelperJSON.get_json_msg(success=False, msg='Sorry!  The classification failed.')            
            return HttpResponse(status=200, content=json_msg, content_type="application/json")

        # --------------------------------------------------------------
        #   Classification Failed
        # --------------------------------------------------------------
        if json_resp.get("success") is False:
            logger.error('Worldmap call returned success = false: %s' % resp.text)
            user_msg = 'Sorry!  The classification failed.<br /><br />(%s)' % json_resp.get('message', 'nada')
            json_msg = MessageHelperJSON.get_json_msg(success=False, msg=user_msg)            
            return HttpResponse(status=200, content=json_msg, content_type="application/json")

        # --------------------------------------------------------------
        #   Looks good, save the update attributed information
        # --------------------------------------------------------------
        f_val = WorldMapToGeoconnectMapLayerMetadataValidationForm(json_resp.get('data', None))
        if not f_val.is_valid():
            logger.error('Classify return data failed validation: %s' % f_val.errors)
            user_msg = 'Sorry!  The classification failed.<br /><br />(%s)' \
                            % json_resp.get('message', f_val.errors)
            json_msg = MessageHelperJSON.get_json_msg(success=False, msg=user_msg)
            return HttpResponse(status=200, content=json_msg, content_type="application/json")

        # --------------------------------------------------------------
        #   Update the WorldMapLayerInfo object's attribute info
        # --------------------------------------------------------------
        worldmap_layerinfo.add_attribute_info(f_val.cleaned_data['attribute_info'])
        worldmap_layerinfo.save()


        # --------------------------------------------------------------
        #   Update the Dataverse metadata -- so that the new icon will be refreshed
        # --------------------------------------------------------------
        
        # Is all this needed, or should there be an API call to only update the image?    
        MetadataUpdater.update_dataverse_with_metadata(worldmap_layerinfo)
        
        #
        #

        msg_params = classify_form.get_params_for_display()

        #msg_params.pop('geoconnect_token', None) # don't want this in the template
        #classify_form = ClassifyLayerForm(**dict(worldmap_layerinfo=worldmap_layerinfo))
        success_msg =  render_to_string('classification/classify_success_msg.html', msg_params)
        d.update(dict(classify_form=classify_form\
                , worldmap_layerinfo=worldmap_layerinfo\
                , success_msg=success_msg#'A new style has been created using attribute <b>%s</b>!' % classify_params.get('attribute', '???')\
                ))
                
        form_content = render_to_string('classification/view_classify_form.html', d\
                                , context_instance=RequestContext(request))
                                
                                
        json_msg = MessageHelperJSON.get_json_msg(success=True
                                            , msg='Success!'
                                            , data_dict={'div_content':form_content}\
                                            )            
        return HttpResponse(status=200, content=json_msg, content_type="application/json")
    
    #    lnk = reverse('view_shapefile'\
    #                    , kwargs=dict(shp_md5=shapefile_md5)\
    #                    )
    #    return HttpResponseRedirect(lnk)
    
    classify_form = ClassifyLayerForm(**dict(worldmap_layerinfo=worldmap_layerinfo))
    #d['form_inline'] = True
    d = dict(classify_form=classify_form, worldmap_layerinfo=worldmap_layerinfo)
    form_content = render_to_string('classification/view_classify_form.html', d\
                            , context_instance=RequestContext(request))
    #print form_content
    #return HttpResponse(form_content)
    #return render_to_response('classification/view_02_single_shapefile.html', d\
    #                        , context_instance=RequestContext(request))
                            
    
    
    print (resp.status_code)
    print (resp.text)
    return HttpResponse('Fail out: %s<pre>%s</pre>' % (resp.status_code, resp.text))
    #wm_response_dict = resp.json() #print()
    #print(wm_response_dict)
    return HttpResponse('post: %s<br />%s' % (request.POST.keys(), classify_url))
    