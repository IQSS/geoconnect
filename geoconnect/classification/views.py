import requests
import logging

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from geo_utils.json_field_reader import MessageHelperJSON
from worldmap_import.models import WorldMapImportAttempt, WorldMapImportFail, WorldMapImportSuccess
from classification.forms import ClassifyLayerForm

logger = logging.getLogger(__name__)

@login_required
def view_classify_layer_form(request, import_success_md5):
    #if not (shapefile_md5 and import_success_md5):
    
    #json_msg = MessageHelperJSON.get_json_msg(success=False
    #                                    , msg='The form submission contains errors'
    #                                    , data_dict={'div_content':'blah'}\
    #                                    )            
    #return HttpResponse(status=400, content=json_msg, content_type="application/json")
    
    # Is the success object md5 available?
    #
    if not import_success_md5:
        json_msg = MessageHelperJSON.get_json_msg(success=False, msg='Parameters are missing')
        return HttpResponse(status=400, content=json_msg, content_type="application/json")
     
    # Is it a POST?   
    #
    if not request.POST:
        json_msg = MessageHelperJSON.get_json_msg(success=False, msg="Use a POST request")    
        return HttpResponse(status=405, content=json_msg, content_type="application/json")
    
    # Does the success object exist?
    #
    try: 
        import_success_object = WorldMapImportSuccess.objects.get(md5=import_success_md5)
    except WorldMapImportSuccess.DoesNotExist:
        json_msg = MessageHelperJSON.get_json_msg(success=False, msg='The WorldMapImportSuccess object does not exist')            
        return HttpResponse(status=410, content=json_msg, content_type="application/json")
        
    # Is the form valid?
    #
    classify_form = ClassifyLayerForm(request.POST, **dict(import_success_object=import_success_object))

    # Invalid forms are status=200 so caught by ajax
    # Form validation will replace the classification div on the page
    if not classify_form.is_valid():
        print ('form not valid')
        d = dict(classify_form=classify_form\
                , import_success_object=import_success_object\
                , error_msg='The form submission contains errors')
        form_content = render_to_string('view_classify_form.html', d\
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
        return HttpResponse(status=400, content=json_msg, content_type="application/json")

    classify_url = classify_form.get_worldmap_classify_api_url()
    
    req = requests.post(classify_url, data=classify_params, timeout=2)
    
    if req.status_code == 200:
        msg_params = classify_form.get_params_for_display()
        #msg_params.pop('geoconnect_token', None) # don't want this in the template
        classify_form = ClassifyLayerForm(**dict(import_success_object=import_success_object))
        success_msg =  render_to_string('classify_success_msg.html', msg_params)
        d = dict(classify_form=classify_form\
                , import_success_object=import_success_object\
                , success_msg=success_msg#'A new style has been created using attribute <b>%s</b>!' % classify_params.get('attribute', '???')\
                )
                
        form_content = render_to_string('view_classify_form.html', d\
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
    
    classify_form = ClassifyLayerForm(**dict(import_success_object=import_success_object))
    #d['form_inline'] = True
    d = dict(classify_form=classify_form, import_success_object=import_success_object)
    form_content = render_to_string('view_classify_form.html', d\
                            , context_instance=RequestContext(request))
    #print form_content
    #return HttpResponse(form_content)
    return render_to_response('view_02_single_shapefile.html', d\
                            , context_instance=RequestContext(request))
                            
    
    
    print (req.status_code)
    print (req.text)
    return HttpResponse('Fail out: %s<pre>%s</pre>' % (req.status_code, req.text))
    #wm_response_dict = req.json() #print()
    #print(wm_response_dict)
    return HttpResponse('post: %s<br />%s' % (request.POST.keys(), classify_url))
    