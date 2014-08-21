import os
import json
import logging

from django.shortcuts import render_to_response

from django.http import HttpResponseRedirect, HttpResponse, Http404

from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from apps.gis_shapefiles.forms import ShapefileSetForm
from apps.gis_shapefiles.models import ShapefileSet, SingleFileInfo
#from apps.gis_shapefiles.shp_services import update_shapefileset_with_metadata
from django.conf import settings
from apps.gis_shapefiles.shapefile_zip_check import ShapefileZipCheck
from apps.gis_shapefiles.models import SHAPEFILE_MANDATORY_EXTENSIONS, WORLDMAP_MANDATORY_IMPORT_EXTENSIONS 

from apps.worldmap_import.models import WorldMapImportAttempt, WorldMapImportSuccess, WorldMapImportFail
from apps.classification.forms import ClassifyLayerForm, ATTRIBUTE_VALUE_DELIMITER

from django.conf import settings

logger = logging.getLogger(__name__)

# Temp while figuring out steps
shapefile_steps = { 10 : ('Examine Dataset', )\
                   #, 20 : ('Choose Shapefile', )\
                   , 30 : ('Inspect Shapefile', )\
                   , 40 : ('Choose Column\Style Info', )\
                    }
def get_shapefile_step_title(k):
    t = shapefile_steps.get(k, None)
    if t:
        return t[0]
    return None

@login_required
def view_delete_files(request):
    if not settings.DEBUG:
        return HttpResponse('only for testing!')
    ShapefileSet.objects.all().delete()
    return HttpResponseRedirect(reverse('view_examine_dataset', args=()))

    
@login_required
def view_delete_worldmap_visualization_attempts(request):
    if not settings.DEBUG:
        return HttpResponse('only for testing!')
    WorldMapImportAttempt.objects.all().delete()
    return HttpResponseRedirect(reverse('view_examine_dataset', args=()))


@login_required
def view_examine_dataset(request):
    """
    Display a list of :model:`gis_shapefiles.ShapefileSet` objects, each linked to a detail page.
    For testing, allow the upload of a new shapefile object.

    **Context** 
    
    ``RequestContext``

    :ShapefileSetForm: Check for a ShapefileSetForm object in the request.POST
    
    **Template:**

    :template:`gis_shapefiles/view_01_examine_zip.html`
    """
    #return HttpResponse('view_google_map')
    d = { 'page_title' : get_shapefile_step_title(10)\
        , 'existing_shapefiles' : ShapefileSet.objects.all()
        
        }
    
    if request.method=='POST':        
        shp_form = ShapefileSetForm(request.POST, request.FILES)
        if shp_form.is_valid():
            shapefile_set = shp_form.save()
            return HttpResponseRedirect(reverse('view_shapefile'\
                                        , kwargs={ 'shp_md5' : shapefile_set.md5 })\
                                    )
            return HttpResponse('saved')            
        else:
            d['Form_Err_Found'] = True
            print shp_form.errors
            #return HttpResponse('blah - not valid')
    else:
        shp_form = ShapefileSetForm

    d['shp_form'] = shp_form 

    return render_to_response('gis_shapefiles/view_01_examine_zip.html', d\
                            , context_instance=RequestContext(request))

#@login_required
def view_shapefile_first_time(request, shp_md5):
    return view_shapefile(request, shp_md5, first_time_notify=True)

#@login_required
def view_shapefile(request, shp_md5, first_time_notify=False):
    ## This is an unreal mess, factor it out similar to SendShapefileService
    """
    Retrieve and view a :model:`gis_shapefiles.ShapefileSet` object

    :shp_md5: unique md5 hash for a :model:`gis_shapefiles.ShapefileSet`
    :template:`gis_shapefiles/view_02_single_shapefile.html`
    """
    logger.debug('view_shapefile')

    d = dict(page_title='View Shapefile')
    
    if first_time_notify:
        d['first_time_notify'] = True
    
    try:
        shapefile_set = ShapefileSet.objects.get(md5=shp_md5)
        d['shapefile_set'] = shapefile_set        
        
    except ShapefileSet.DoesNotExist:
        logger.error('Shapefile not found for hash: %s' % shp_md5)
        raise Http404('Shapefile not found.')
    
    logger.debug('shapefile_set: %s' % shapefile_set)
    

    """
    Early pass: Move this logic out of view
    """
    if not shapefile_set.zipfile_checked:
        logger.debug('zipfile_checked NOT checked')

        logger.debug('fname: %s' % shapefile_set.get_dv_file_fullpath())
        #zip_checker = ShapefileZipCheck(shapefile_set.dv_file, **{'is_django_file_field': True})
        #zip_checker = ShapefileZipCheck(os.path.join(settings.MEDIA_ROOT, shapefile_set.dv_file.name))
        zip_checker = ShapefileZipCheck(shapefile_set.get_dv_file_fullpath())
        zip_checker.validate()
        list_of_shapefile_set_names = zip_checker.get_shapefile_setnames()

        # Error: No shapefiles found
        #
        if list_of_shapefile_set_names is None:
            logger.debug('Error: No shapefiles found')
            
            shapefile_set.has_shapefile = False
            shapefile_set.zipfile_checked = True
            shapefile_set.name = '(not a shapefile)'
            shapefile_set.save()
            d['Err_Found'] = True
            d['Err_No_Shapefiles_Found'] = True
            d['zip_name_list'] = zip_checker.get_zipfile_names()
            d['WORLDMAP_MANDATORY_IMPORT_EXTENSIONS'] = WORLDMAP_MANDATORY_IMPORT_EXTENSIONS
            zip_checker.close_zip()        
            return render_to_response('gis_shapefiles/view_02_single_shapefile.html', d\
                                    , context_instance=RequestContext(request))

        # Error: More than one shapefile in the .zip
        #
        elif len(list_of_shapefile_set_names) > 1:      # more than one shapefile is in this zip
            logger.debug('Error: More than one shapefile in the .zip')
            
            shapefile_set.has_shapefile = False
            shapefile_set.zipfile_checked = True
            shapefile_set.save()
            d['Err_Found'] = True
            d['Err_Multiple_Shapefiles_Found'] = True
            d['list_of_shapefile_set_names'] = list_of_shapefile_set_names
            d['zip_name_list'] = zip_checker.get_zipfile_names()
            #d['WORLDMAP_MANDATORY_IMPORT_EXTENSIONS'] = WORLDMAP_MANDATORY_IMPORT_EXTENSIONS
            zip_checker.close_zip()        
            return render_to_response('gis_shapefiles/view_02_single_shapefile.html', d\
                                    , context_instance=RequestContext(request))

        # Load the single shapefile
        #
        elif len(list_of_shapefile_set_names) == 1:
            logger.debug('Load the single shapefile')
            
            shapefile_set.has_shapefile = True
            shapefile_set.zipfile_checked = True
            shapefile_set.save()
            #shapefile_set.name = os.path.basename(list_of_shapefile_set_names[0])
            (success, err_msg_or_none) = zip_checker.load_shapefile_from_open_zip(list_of_shapefile_set_names[0], shapefile_set)
            print 'here'
            if not success:
                print 'here - err'
                d['Err_Found'] = True
                d['Err_Msg'] = err_msg_or_none
                shapefile_set.has_shapefile = False
                shapefile_set.save()
                logger.error('Shapefile not loaded. (%s)' % shp_md5)
                return render_to_response('gis_shapefiles/view_02_single_shapefile.html', d\
                                        , context_instance=RequestContext(request))

            zip_checker.close_zip()        
            return render_to_response('gis_shapefiles/view_02_single_shapefile.html', d\
                                    , context_instance=RequestContext(request))
            
        
        
    if not shapefile_set.has_shapefile:
        logger.debug('No shapefile found in .zip')
        
        d['Err_Found'] = True
        d['Err_No_Shapefiles_Found'] = True
        #d['zip_name_list'] = zip_checker.get_zipfile_names()
        d['WORLDMAP_MANDATORY_IMPORT_EXTENSIONS'] = WORLDMAP_MANDATORY_IMPORT_EXTENSIONS
        return render_to_response('gis_shapefiles/view_02_single_shapefile.html', d\
                                , context_instance=RequestContext(request))
    
    
                            
    
    logger.debug('Has an import been attempted?')
    latest_import_attempt = WorldMapImportAttempt.get_latest_attempt(shapefile_set)

    if latest_import_attempt:
        logger.debug('latest_import_attempt: %s' % latest_import_attempt )
        import_success_object = latest_import_attempt.get_success_info()
        if import_success_object:
            classify_form = ClassifyLayerForm(**dict(import_success_object=import_success_object))
            #d['form_inline'] = True
            d['classify_form'] = classify_form
            d['ATTRIBUTE_VALUE_DELIMITER'] = ATTRIBUTE_VALUE_DELIMITER
            
                
                    
        d['import_success_object'] = import_success_object
        
        logger.debug('import_success_object: %s' % d['import_success_object'] ) #WorldMapImportSuccess.objects.filter(import_attempt__gis_data_file=shapefile_set)
        d['import_fail_list'] =latest_import_attempt.get_fail_info() 
        
        logger.debug('import_fail_list: %s' % d['import_fail_list'] ) 
        #WorldMapImportFail.objects.filter(import_attempt__gis_data_file=shapefile_set)
    

    
    return render_to_response('gis_shapefiles/view_02_single_shapefile.html', d\
                            , context_instance=RequestContext(request))
                            
   