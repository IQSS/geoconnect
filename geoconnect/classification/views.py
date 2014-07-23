from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template import RequestContext

from worldmap_import.models import WorldMapImportAttempt, WorldMapImportFail, WorldMapImportSuccess
from classification.forms import ClassifyLayerForm

def view_classify_layer_form(request, import_success_md5):
    if not request.POST:
        return HttpResponse('should be a POST!')
        
    try: 
        import_success_object = WorldMapImportSuccess.objects.get(md5=import_success_md5)
    except WorldMapImportSuccess.DoesNotExist:
        raise HttpResponse('WorldMapImportSuccess does not exist, redo as ajax err message')
    
    classify_form = ClassifyLayerForm(request.POST, **dict(import_success_object=import_success_object))
    
    
                                 
    if not classify_form.is_valid():
        return HttpResponse('invalid form')

    classify_parms = classify_form.get_params_dict_for_classification()
    print(classify_parms)
    return HttpResponse('post: %s' % request.POST.keys())
    