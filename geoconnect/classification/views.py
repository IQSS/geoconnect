import requests

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template import RequestContext
from django.core.urlresolvers import reverse

from worldmap_import.models import WorldMapImportAttempt, WorldMapImportFail, WorldMapImportSuccess
from classification.forms import ClassifyLayerForm

def view_classify_layer_form(request, shapefile_md5, import_success_md5):
    if not (shapefile_md5 and import_success_md5):
        raise Http404('view_classify_layer_form: missing params')

    if not request.POST:
        return HttpResponse('should be a POST!')
        
    try: 
        import_success_object = WorldMapImportSuccess.objects.get(md5=import_success_md5)
    except WorldMapImportSuccess.DoesNotExist:
        raise HttpResponse('WorldMapImportSuccess does not exist, redo as ajax err message')
    
    classify_form = ClassifyLayerForm(request.POST, **dict(import_success_object=import_success_object))
    
                        
    if not classify_form.is_valid():
        return HttpResponse('invalid form')

    classify_params = classify_form.get_params_dict_for_classification()
    if classify_params is None:
        return HttpResponse('bad params')
    print(classify_params)
    
    classify_url = classify_form.get_worldmap_classify_api_url()
    
    req = requests.post(classify_url, data=classify_params, timeout=2)
    if req.status_code == 200:
        lnk = reverse('view_shapefile'\
                        , kwargs=dict(shp_md5=shapefile_md5)\
                        )
        return HttpResponseRedirect(lnk)
        
    print (req.status_code)
    print (req.text)
    return HttpResponse('Fail out: %s<pre>%s</pre>' % (req.status_code, req.text))
    #wm_response_dict = req.json() #print()
    #print(wm_response_dict)
    return HttpResponse('post: %s<br />%s' % (request.POST.keys(), classify_url))
    