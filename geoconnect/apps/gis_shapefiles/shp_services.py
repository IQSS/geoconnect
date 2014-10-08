import json
import urllib2

from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

from dataverse_info.forms import DataverseInfoValidationForm

from geo_utils.msg_util import *

from apps.gis_shapefiles.models import ShapefileInfo
from apps.worldmap_connect.models import WorldMapImportAttempt, WorldMapImportSuccess

import logging
logger = logging.getLogger(__name__)



def get_shapefile_from_dv_api_info(dv_session_token, dataverse_info_dict):
    """Using Dataverse API information, create a :model:`gis_shapefiles.ShapefileInfo' object.  This function should only receive successful responses.
    """
    assert(dv_session_token, not None)
    assert(len(dv_session_token), not 0)
    assert(type(dataverse_info_dict), dict)

    #------------------------------
    # (1) Validate the data
    #------------------------------
    #dataverse_info_dict.update({'datafile_id':None})   # for testing
    validation_form = DataverseInfoValidationForm(dataverse_info_dict)
    if not validation_form.is_valid():
        errs = [ '%s: %s' % (k, v) for k,v in validation_form.errors.items()]
        print (errs)
        raise Exception('\n'.join(errs))
    
    #------------------------------
    # (2) Look for existing shapefiles in the database
    #    ShapefileInfo objects are routinely deleted, but if file is already here, use it
    #------------------------------
    params_for_existing_check = dict(datafile_id=dataverse_info_dict.get('datafile_id', -1)\
                                    , dv_user_id=dataverse_info_dict.get('dv_user_id', -1)\
                                    )
    existing_sets = ShapefileInfo.objects.filter(**params_for_existing_check\
                                ).values_list('id', flat=True\
                                ).order_by('created')

    existing_shapefile_info_ids = list(existing_sets)
    msgt('existing_shapefile_info_ids: %s' % existing_shapefile_info_ids)
    
    # add dv_session_token token to dataverse_info_dict
    #
    dataverse_info_dict['dv_session_token'] = dv_session_token
    
    #------------------------------
    # (3) Existing ShapefileInfo(s) found:
    #  (a) Update the ShapefileInfo object
    #  (b) Delete other groups ShapefileInfo object for this datafile and user
    #  (c) Return the md5
    #------------------------------
    if len(existing_shapefile_info_ids) > 1:
        
        # pop the last ShapefileInfo id off the list of existing_shapefile_info_ids
        shp_id = existing_shapefile_info_ids.pop()

        # delete the rest
        if len(existing_sets) > 0:
            ShapefileInfo.objects.filter(id__in=existing_shapefile_info_ids).delete()   # delete older ShapefileInfo(s)
        
    msgt('(4) Get or create a new ShapefileInfo object')

    #------------------------------
    # (4) Get or create a new ShapefileInfo object
    #------------------------------
    try:
        # Existing ShapefileInfo:
        #   (1) Assume file is already saved
        #   (2) update the data
        #
        shapefile_info = ShapefileInfo.objects.get(**params_for_existing_check)

        for key, value in dataverse_info_dict.iteritems():
            setattr(shapefile_info, key, value)
        
        # Save
        shapefile_info.save()

        # If the file is still available, continue on
        if shapefile_info.is_dv_file_available():
            return shapefile_info.md5
    
        # But the file isn't there!!  Delete ShapefileInfo and make a new one
        shapefile_info.delete()
        
    except ShapefileInfo.DoesNotExist:
        pass
    except:
        raise Exception('Failed to Get or create a new ShapefileInfo object')

    msg('new file')
    
    #------------------------------
    # New shapefile info, create object and attach file
    #------------------------------
    shapefile_info = ShapefileInfo(**dataverse_info_dict)
    shapefile_info.save()
                
    #------------------------------
    # Download and attach file
    #------------------------------
    datafile_download_url = dataverse_info_dict.get('datafile_download_url', '')
    datafile_filename = dataverse_info_dict.get('datafile_label', '')
    
    img_temp = NamedTemporaryFile(delete=True)
    img_temp.write(urllib2.urlopen(datafile_download_url).read())
    img_temp.flush()

    shapefile_info.dv_file.save(datafile_filename, File(img_temp))
    shapefile_info.save()
    
    return shapefile_info.md5


def get_successful_worldmap_attempt_from_shapefile(shapefile_info):
    """
    Given a ShapefileInfo object, check for and return a WorldMapImportSuccess object, if available

    :param shapefile_info: ShapefileInfo object
    :return: WorldMapImportSuccess object or None
    """
    assert(type(shapefile_info), ShapefileInfo)

    latest_import_attempt = WorldMapImportAttempt.get_latest_attempt(shapefile_info)
    if latest_import_attempt:
        import_success_object = latest_import_attempt.get_success_info()
        if type(import_success_object) is WorldMapImportSuccess:
            return import_success_object
    return None