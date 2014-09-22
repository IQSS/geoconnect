import json
import urllib2

from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

from apps.gis_shapefiles.models import ShapefileInfo
from apps.worldmap_import.models import WorldMapImportAttempt, WorldMapImportSuccess

import logging
logger = logging.getLogger(__name__)


DV_API_REQ_KEYS = ['created', 'datafile_download_url', 'datafile_expected_md5_checksum', 'datafile_id', 'datafile_label', 'datafile_type', 'dataset_description', 'dataset_id', 'dataset_name', 'dataset_version_id', 'dv_id', 'dataverse_name', 'dv_user_email', 'dv_user_id', 'dv_username', 'filename', 'filesize', 'return_to_dataverse_url' ]
NON_SHAPEFILE_SET_PARAMS = [ 'datafile_download_url', 'filename', 'filesize', 'created']

def get_shapefile_from_dv_api_info(dv_session_token, shp_dict):
    """Using Dataverse API information, create a :model:`gis_shapefiles.ShapefileInfo' object.  This function should only receive successful responses.
    
    :param shp_dict: dict containing response from the Dataverse API
    
    example: {
             'datafile_label': 'income_in_boston_gui_1.zip'
            , 'dv_user_email': 'raman_prasad@harvard.ed'
            , 'dv_username': 'raman'
            , 'datafile_id': 1
            , 'datafile_type': '--file-type--'
            , 'datafile_expected_md5_checksum' : '1007330fd9c833d2aac518bbbb5354d9'
            , 'dataset_description': ''
            , 'filename': 'income_in_boston_gui_1.zip'
            , 'has_gis_data': True
            , 'dv_user_id': 1
            , 'created': '2014-06-02 17:32:43.802018+00:00'
            , 'dataset_version_id': 1
            , 'dataset_id': 1
            , 'dataset_name': 'Boston Income data'
            , 'filesize': 498556\
            , 'datafile_download_url' : 'http://127.0.0.1:8090/media/datafile/2014/06/02/boston_income.zip'
            , 'return_to_dataverse_url' : http://localhost:8080/dataset.xhtml?id=245&versionId=26
            }
    """
    if shp_dict is None:
        return None

    if not all(rkey in shp_dict.keys() for rkey in DV_API_REQ_KEYS):
        missing_keys = [rkey for rkey in DV_API_REQ_KEYS if rkey not in shp_dict.keys() ]
        raise Exception('Not all keys found in %s' % missing_keys)

    datafile_download_url = shp_dict.get('datafile_download_url', '')
    datafile_filename = shp_dict.get('filename', '')
    for non_essential_param in NON_SHAPEFILE_SET_PARAMS:
        if shp_dict.has_key(non_essential_param):
            shp_dict.pop(non_essential_param)
    
    for k in shp_dict.keys():
        print '%s->%s' % (k, shp_dict[k])
    
    
    #------------------------------
    # Check for existing shapefile sets based on the kwargs
    #------------------------------
    params_for_existing_check = dict(datafile_id=shp_dict.get('datafile_id', -1)\
                                    , dv_user_id=shp_dict.get('dv_user_id', -1)\
                                    )
    existing_sets = ShapefileInfo.objects.filter(**params_for_existing_check\
                                ).values_list('md5', flat=True\
                                ).order_by('created')

    existing_sets = list(existing_sets)
    
    print '-' *40
    print 'Existing set count: %s' % len(existing_sets)
    
    #------------------------------
    # Existing ShapefileInfo(s) found:
    #  (a) Update the dv_session_token
    #  (b) Delete other groups ShapefileInfo object for this datafile and user
    #  (c) Return the md5
    #------------------------------
    if len(existing_sets) > 0:
        shp_md5 = existing_sets.pop()

        # Update the dv_session_token
        try:
            shp_set = ShapefileInfo.objects.get(md5=shp_md5)
        except ShapefileInfo.DoesNotExist:
            # serious error!
            return None
            
        shp_set.dv_session_token = dv_session_token
        shp_set.return_to_dataverse_url = shp_dict.get('return_to_dataverse_url', '')
        shp_set.save()
        
        if len(existing_sets) > 0:
            ShapefileInfo.objects.filter(md5__in=existing_sets).delete()   # delete older ShapefileInfo(s)
        return shp_md5

    #------------------------------
    # Make a new ShapefileInfo
    #------------------------------
    if dv_session_token:
        shp_dict['dv_session_token'] = dv_session_token
    shapefile_info = ShapefileInfo(**shp_dict)
    shapefile_info.save()
    
    # Download and attach file
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