import logging

from django.shortcuts import render

from django.http import HttpResponseRedirect, HttpResponse, Http404

from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from django.conf import settings

from gc_apps.geo_utils.template_constants import ZIPCHECK_NO_SHAPEFILES_FOUND,\
        ZIPCHECK_MULTIPLE_SHAPEFILES,\
        ZIPCHECK_NO_FILE_TO_CHECK,\
        ZIPCHECK_FAILED_TO_PROCCESS_SHAPEFILE

from gc_apps.gis_shapefiles.forms import ShapefileInfoForm
from gc_apps.gis_shapefiles.models import ShapefileInfo, WORLDMAP_MANDATORY_IMPORT_EXTENSIONS
from gc_apps.gis_shapefiles.shapefile_zip_check import ShapefileZipCheck
from gc_apps.worldmap_connect.send_shapefile_service import SendShapefileService
from gc_apps.worldmap_layers.models import WorldMapLayerInfo

from shared_dataverse_information.layer_classification.forms import \
    ClassifyLayerForm, ATTRIBUTE_VALUE_DELIMITER
from gc_apps.gis_tabular.forms_delete import DeleteMapForm
from gc_apps.gis_tabular.models import TabularFileInfo
from gc_apps.gis_tabular.forms import SELECT_LABEL


from gc_apps.geo_utils.geoconnect_step_names import GEOCONNECT_STEP_KEY,\
    STEP1_EXAMINE, STEP2_STYLE,\
    PANEL_TITLE_MAP_DATA_FILE, PANEL_TITLE_STYLE_MAP

from gc_apps.geo_utils.view_util import get_common_lookup

logger = logging.getLogger(__name__)


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
        else:
            d['Form_Err_Found'] = True
            #print shp_form.errors
            #return HttpResponse('blah - not valid')
    else:
        shp_form = ShapefileInfoForm

    d['shp_form'] = shp_form

    return render(request, 'gis_shapefiles/view_01_examine_zip.html', d)


def view_classify_shapefile(request, worldmap_layerinfo, first_time_notify=False):
    """Called by 'view_shapefile' -- no direct url associated with this view"""

    assert isinstance(worldmap_layerinfo, WorldMapLayerInfo),\
        "worldmap_layerinfo must be an instance of WorldMapLayerInfo"

    d = get_common_lookup(request)
    d['page_title'] = PANEL_TITLE_STYLE_MAP
    d[GEOCONNECT_STEP_KEY] = STEP2_STYLE

    classify_form = ClassifyLayerForm(**worldmap_layerinfo.get_dict_for_classify_form())

    shapefile_info = worldmap_layerinfo.get_gis_data_info()
    if not shapefile_info:
        raise Http404('shapefile md5 not found!')

    delete_form = DeleteMapForm.get_form_with_initial_vals(worldmap_layerinfo)

    d.update(worldmap_layerinfo.get_core_data_dict_for_views())

    d['gis_data_info'] = shapefile_info
    #d['shapefile_info'] = shapefile_info
    d['classify_form'] = classify_form
    d['delete_form'] = delete_form

    d['ATTRIBUTE_VALUE_DELIMITER'] = ATTRIBUTE_VALUE_DELIMITER
    d['first_time_notify'] = first_time_notify
    d['SELECT_LABEL'] = SELECT_LABEL

    return render(request, 'shapefiles/main_outline_shp.html', d)



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
    :template:`shapefiles/main_outline_shp.html`
    """
    logger.debug('-' * 40)
    logger.debug('view_shapefile')
    # -------------------------------------------
    # Flags for template - Is this the first time the file is being visualized?
    # -------------------------------------------
    first_time_notify = kwargs.get('first_time_notify', False)


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
    d['gis_data_info'] = shapefile_info
    d['shapefile_info'] = shapefile_info
    d['page_title'] = PANEL_TITLE_MAP_DATA_FILE
    d['WORLDMAP_SERVER_URL'] = settings.WORLDMAP_SERVER_URL
    d[GEOCONNECT_STEP_KEY] = STEP1_EXAMINE
    if first_time_notify:
        d['first_time_notify'] = True

    # -------------------------------------------
    # Early pass: Validate that this .zip is a shapefile--a single shapefile
    #    - Should we move this out?  Check being done at Dataverse
    #    - Also, no need to move the file if viz already exists
    # -------------------------------------------
    if not shapefile_info.zipfile_checked:
        logger.debug('zipfile_checked NOT checked')

        logger.debug('fname: %s' % shapefile_info.get_dv_file_fullpath())

        zip_checker = ShapefileZipCheck(shapefile_info.dv_file, **{'is_django_file_field': True})
        #zip_checker = ShapefileZipCheck(shapefile_info.get_dv_file_fullpath())
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
            return render(request, 'shapefiles/main_outline_shp.html', d)

    # -------------------------------------------
    # The examination failed
    # No shapefile was found in this .zip
    # -------------------------------------------
    if not shapefile_info.has_shapefile:
        logger.debug('No shapefile found in .zip')

        d['Err_Found'] = True
        d['Err_No_Shapefiles_Found'] = True
        d['WORLDMAP_MANDATORY_IMPORT_EXTENSIONS'] = WORLDMAP_MANDATORY_IMPORT_EXTENSIONS
        return render(request, 'shapefiles/main_outline_shp.html', d)


    return render(request, 'shapefiles/main_outline_shp.html', d)



def view_zip_checker_error(request, shapefile_info, zip_checker, template_params):
    """
    Used to display a message when an error is detected
    while examining the zipped Shapefile
    """
    assert isinstance(zip_checker, ShapefileZipCheck),\
        "zip_checker is not a ShapefileZipCheck object"
    assert zip_checker.has_err, "Only use this when 'has_err is True'"

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

    else:
        d['Err_Msg'] = zip_checker.error_msg

    # Send error to user
    return render(request, 'shapefiles/main_outline_shp.html', d)
