"""
Help format parameters related to the worldmap_connect.models

"""
import logging
from django.conf import settings

from apps.worldmap_connect.models import WorldMapLayerInfo, WorldMapImportAttempt
from apps.gis_basic_file.dataverse_info_service import get_dataverse_info_dict

from shared_dataverse_information.shared_form_util.format_form_errors import format_errors_as_text
from shared_dataverse_information.shapefile_import.forms import ShapefileImportDataForm

logger = logging.getLogger(__name__)

def get_params_for_worldmap_connect(wm_import_attempt, geoconnect_token=None):
    """
    Use the ShapefileImportDataForm to prepare parameters for the WorldMap import request.

    Note: The "geoconnect_token" parameter is provided by the class calling the function.
        At this point it is worldmap_connect.WorldMapImporter.
        if a geoconnect_token is not supplied, it will not be included in the params dict

    :param geoconnect_token: key used to access the WorldMap API
    :type geoconnect_token: string or None
    :returns: parameters formatted to call the WorldMap import API.
    """
    logger.debug('get_params_for_worldmap_connect')

    assert type(wm_import_attempt) is WorldMapImportAttempt, "wm_import_attempt must be a WorldMapImportAttempt object"
    assert wm_import_attempt.gis_data_file is not None, "wm_import_attempt.gis_data_file cannot be None"

    # Prepare initial data
    #
    #   - Give all parameters from WorldMapImportAttempt object to the ShapefileImportDataForm
    #   - ShapefileImportDataForm will validate and give back the needed values
    #
    f = ShapefileImportDataForm(wm_import_attempt.__dict__)
    if not f.is_valid():
        form_errs_as_text = format_errors_as_text(f)
        raise ValueError('WorldMapImportAttempt does not have correct params for ShapefileImportDataForm: \n%s' % form_errs_as_text)
    
    # Add basic data clenaed by ShapefileImportDataForm
    #     
    params_dict = f.cleaned_data
    
    # Add dataverse info to the params_dict
    #
    dataverse_info_dict = get_dataverse_info_dict(wm_import_attempt.gis_data_file)
    if dataverse_info_dict is None:
        raise ValueError('Failed to format DataverseInfo params using wm_import_attempt.gis_data_file')
        
    params_dict.update(dataverse_info_dict)

    # (optional) Add the WorldMap shared token value
    #
    if geoconnect_token is not None:
        params_dict[settings.WORLDMAP_TOKEN_NAME_FOR_DV] = geoconnect_token

    # Return the parameters
    #
    return params_dict

"""
from apps.worldmap_connect.models import WorldMapLayerInfo, WorldMapImportAttempt
from shapefile_import.forms import ShapefileImportDataForm

t = WorldMapImportAttempt.objects.all()[0]
f = ShapefileImportDataForm(t.__dict__)
f.is_valid()


from shared_form_util.format_form_errors import format_errors_as_text
f = ShapefileImportDataForm(dict(abstract='blah',dv_user_email='myemail'))
errs = None
if not f.is_valid():
    errs = format_errors_as_text(f)


    
print (errs)

"""


