import logging

from django.shortcuts import render_to_response

from django.http import HttpResponseRedirect, HttpResponse, Http404

from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from django.conf import settings

from geo_utils.template_constants import ZIPCHECK_NO_SHAPEFILES_FOUND,\
        ZIPCHECK_MULTIPLE_SHAPEFILES,\
        ZIPCHECK_NO_FILE_TO_CHECK,\
        ZIPCHECK_FAILED_TO_PROCCESS_SHAPEFILE

from apps.gis_shapefiles.forms import ShapefileInfoForm
from apps.gis_shapefiles.models import ShapefileInfo, WORLDMAP_MANDATORY_IMPORT_EXTENSIONS
from apps.gis_shapefiles.shapefile_zip_check import ShapefileZipCheck
from apps.worldmap_connect.send_shapefile_service import SendShapefileService
from apps.worldmap_layers.models import WorldMapLayerInfo


#from apps.gis_shapefiles.shp_services import get_successful_worldmap_attempt_from_shapefile


from apps.gis_shapefiles.shapefile_examine_util import ShapefileExamineUtil

from apps.worldmap_connect.models import WorldMapImportAttempt
from apps.gis_shapefiles.shp_services import add_worldmap_layerinfo_if_exists

from shared_dataverse_information.layer_classification.forms import \
    ClassifyLayerForm, ATTRIBUTE_VALUE_DELIMITER
from apps.worldmap_connect.form_delete import DeleteMapForm
from apps.gis_tabular.models import TabularFileInfo

from geo_utils.geoconnect_step_names import GEOCONNECT_STEP_KEY,\
    STEP1_EXAMINE, STEP2_STYLE
from geo_utils.view_util import get_common_lookup

logger = logging.getLogger(__name__)


@login_required
def view_delete_files(request):
    if not settings.DEBUG:
        return HttpResponse('only for testing!')
    ShapefileInfo.objects.all().delete()
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
    For TESTING, allow the upload of a new shapefile object.

    Display a list of "ShapefileInfo" objects, each linked to a detail page.

    - Check for a ShapefileInfoForm object in the request.POST
    - Template: "gis_shapefiles/view_01_examine_zip.html"
    """
    #return HttpResponse('view_google_map')
    d = { 'page_title' : 'Shapefiles: Test Upload Page'\
        , 'existing_shapefiles' : ShapefileInfo.objects.all()
        , 'existing_tabular_files' : TabularFileInfo.objects.all()
        }

    if request.method=='POST':
        shp_form = ShapefileInfoForm(request.POST, request.FILES)
        if shp_form.is_valid():
            shapefile_info = shp_form.save()
            return HttpResponseRedirect(reverse('view_shapefile'\
                                        , kwargs={ 'shp_md5' : shapefile_info.md5 })\
                                    )
            return HttpResponse('saved')
        else:
            d['Form_Err_Found'] = True
            #print shp_form.errors
            #return HttpResponse('blah - not valid')
    else:
        shp_form = ShapefileInfoForm

    d['shp_form'] = shp_form

    return render_to_response('gis_shapefiles/view_01_examine_zip.html', d\
                            , context_instance=RequestContext(request))


def view_classify_shapefile(request, worldmap_layerinfo, first_time_notify):
    """Called by 'view_shapefile' -- no url associated with this view"""

    assert isinstance(worldmap_layerinfo, WorldMapLayerInfo),\
        "worldmap_layerinfo must be an instance of WorldMapLayerInfo"

    d = get_common_lookup(request)
    d['page_title'] = 'Style Map'
    d[GEOCONNECT_STEP_KEY] = STEP2_STYLE

    classify_form = ClassifyLayerForm(**worldmap_layerinfo.get_dict_for_classify_form())

    shapefile_info = worldmap_layerinfo.get_gis_data_info()
    if not shapefile_info:
        raise Http404('shapefile md5 not found!')

    delete_form = DeleteMapForm(initial=dict(gis_data_file_md5=shapefile_info.md5\
                                    , worldmap_layer_info_md5=worldmap_layerinfo.md5)\
                                )

    d.update(worldmap_layerinfo.get_core_data_dict_for_views())

    d['shapefile_info'] = shapefile_info
    d['classify_form'] = classify_form
    d['delete_form'] = delete_form

    d['ATTRIBUTE_VALUE_DELIMITER'] = ATTRIBUTE_VALUE_DELIMITER
    d['first_time_notify'] = first_time_notify

    return render_to_response('gis_shapefiles/view_shapefile_overview.html', d\
                        , context_instance=RequestContext(request))



def view_shapefile_first_time(request, shp_md5):
    return view_shapefile(request, shp_md5, first_time_notify=True)


#@login_required
def view_shapefile(request, shp_md5, **kwargs):
    """
    (1) Does a map of this shapefile exist in the db?

    (2) Does a map of this shapefile exist in WorldMap?

    (3) Show the initial page with "Visualize" button

    This is fantastically long and messy -- need to break it up

    Retrieve and view a :model:`gis_shapefiles.ShapefileInfo` object

    :shp_md5: unique md5 hash for a :model:`gis_shapefiles.ShapefileInfo`
    :template:`gis_shapefiles/view_shapefile_overview.html`
    """
    logger.debug('-' * 40)
    logger.debug('view_shapefile')
    # -------------------------------------------
    # Flags for template - Is this the first time the file is being visualized?
    # -------------------------------------------
    first_time_notify = kwargs.get('first_time_notify', False)
    if first_time_notify:
        d['first_time_notify'] = True


    # (1) and (2) - Does a layer already exist
    #
    shp_service = SendShapefileService(**dict(shp_md5=shp_md5))
    if shp_service.flow1_does_map_already_exist():
        worldmap_layerinfo = shp_service.get_worldmap_layerinfo()
        if worldmap_layerinfo is None:
            return HttpResponse('<br />'.join(shp_service.err_msgs))
        else:
            return view_classify_shapefile(request, worldmap_layerinfo, first_time_notify)


    # -------------------------------------------
    # Attempt to retrieve the shapefile information
    # -------------------------------------------
    try:
        shapefile_info = ShapefileInfo.objects.get(md5=shp_md5)
    except ShapefileInfo.DoesNotExist:
        logger.error('Shapefile not found for hash: %s' % shp_md5)
        raise Http404('Shapefile not found.')

    # -------------------------------------------
    # Gather common parameters for the template
    # -------------------------------------------
    d = get_common_lookup(request)
    d['shapefile_info'] = shapefile_info
    d['page_title'] = 'Examine Shapefile'
    d['WORLDMAP_SERVER_URL'] = settings.WORLDMAP_SERVER_URL
    d[GEOCONNECT_STEP_KEY] = STEP1_EXAMINE

    # -------------------------------------------
    # Early pass: Validate that this .zip is a shapefile--a single shapefile
    #    - Should we move this out?  Check being done at Dataverse
    #    - Also, no need to move the file if viz already exists
    # -------------------------------------------
    if not shapefile_info.zipfile_checked:
        logger.debug('zipfile_checked NOT checked')

        logger.debug('fname: %s' % shapefile_info.get_dv_file_fullpath())
        #zip_checker = ShapefileZipCheck(shapefile_info.dv_file, **{'is_django_file_field': True})
        #zip_checker = ShapefileZipCheck(os.path.join(settings.MEDIA_ROOT, shapefile_info.dv_file.name))

        zip_checker = ShapefileZipCheck(shapefile_info.get_dv_file_fullpath())
        zip_checker.validate()

        # -----------------------------
        # Error: No shapefiles found
        #   Show error message
        # -----------------------------
        if zip_checker.has_err:
            return view_zip_checker_error(request, shapefile_info, zip_checker, d)

        # -----------------------------
        # Load the single shapefile
        # -----------------------------
        logger.debug('Load the single shapefile')

        shapefile_info.has_shapefile = True
        shapefile_info.zipfile_checked = True
        shapefile_info.save()

        list_of_shapefile_set_names = zip_checker.get_shapefile_setnames()
        success = zip_checker.load_shapefile_from_open_zip(list_of_shapefile_set_names[0], shapefile_info)
        if not success:
            d['Err_Found'] = True
            if zip_checker.err_type == ZIPCHECK_FAILED_TO_PROCCESS_SHAPEFILE:
                d['Err_Shapefile_Could_Not_Be_Opened'] = True
                d['zip_name_list'] = zip_checker.get_zipfile_names()
            else:
                d['Err_Msg'] = zip_checker.err_msg

            shapefile_info.has_shapefile = False
            shapefile_info.save()
            logger.error('Shapefile not loaded. (%s)' % shp_md5)
            zip_checker.close_zip()
            return render_to_response('gis_shapefiles/view_shapefile_overview.html', d\
                                        , context_instance=RequestContext(request))

    # -------------------------------------------
    # The examination failed
    # No shapefile was found in this .zip
    # -------------------------------------------
    if not shapefile_info.has_shapefile:
        logger.debug('No shapefile found in .zip')

        d['Err_Found'] = True
        d['Err_No_Shapefiles_Found'] = True
        d['WORLDMAP_MANDATORY_IMPORT_EXTENSIONS'] = WORLDMAP_MANDATORY_IMPORT_EXTENSIONS
        return render_to_response('gis_shapefiles/view_shapefile_overview.html', d\
                                , context_instance=RequestContext(request))


    return render_to_response('gis_shapefiles/view_shapefile_overview.html', d\
                            , context_instance=RequestContext(request))



def view_zip_checker_error(request, shapefile_info, zip_checker, template_params):
    """
    Used to display a message when an error is detected
    while examining the zipped Shapefile
    """
    assert isinstance(zip_checker, ShapefileZipCheck),\
        "zip_checker is not a ShapefileZipCheck object"
    assert zip_checker.err_detected, "Only use this when 'err_detected is True'"

    d = template_params

    # Update shapefile_info object
    shapefile_info.has_shapefile = False
    shapefile_info.zipfile_checked = True

    # Update for user template
    d['Err_Found'] = True

    error_type = zip_checker.error_type

    '''
    ZIPCHECK_FAILED_TO_PROCCESS_SHAPEFILE = 'ZIPCHECK_FAILED_TO_PROCCESS_SHAPEFILE'
    '''
    if error_type == ZIPCHECK_NO_FILE_TO_CHECK:

        # Update shapefile_info object
        shapefile_info.name = '(no file to check)'
        shapefile_info.save()

        # Update for user template
        d['Err_No_File_Found'] = True
        #d['zip_name_list'] = zip_checker.get_zipfile_names()
        #d['WORLDMAP_MANDATORY_IMPORT_EXTENSIONS'] = WORLDMAP_MANDATORY_IMPORT_EXTENSIONS
        zip_checker.close_zip()

    elif error_type == ZIPCHECK_NO_SHAPEFILES_FOUND:

        # Update shapefile_info object
        shapefile_info.name = '(not a shapefile)'
        shapefile_info.save()

        # Update for user template
        d['Err_No_Shapefiles_Found'] = True
        d['zip_name_list'] = zip_checker.get_zipfile_names()
        d['WORLDMAP_MANDATORY_IMPORT_EXTENSIONS'] = WORLDMAP_MANDATORY_IMPORT_EXTENSIONS
        zip_checker.close_zip()

    elif error_type == ZIPCHECK_MULTIPLE_SHAPEFILES:
        # Error: More than one shapefile in the .zip
        #
        shapefile_info.name = '(multiple shapefiles found)'
        shapefile_info.save()

        # Update for user template
        d['Err_Multiple_Shapefiles_Found'] = True
        d['list_of_shapefile_set_names'] = zip_checker.get_shapefile_setnames()
        d['zip_name_list'] = zip_checker.get_zipfile_names()
        zip_checker.close_zip()

    # Send error to user
    return render_to_response('gis_shapefiles/view_shapefile_overview.html', d\
                            , context_instance=RequestContext(request))
