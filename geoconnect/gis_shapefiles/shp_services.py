import json
import urllib2

from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

from gis_shapefiles.models import ShapefileSet
from gis_shapefiles.shapefile_zip_check import ShapefileZipCheck
import shapefile

import logging
logger = logging.getLogger(__name__)


DV_API_REQ_KEYS = ['created', 'datafile_download_url', 'datafile_expected_md5_checksum', 'datafile_id', 'datafile_label', 'datafile_type', 'dataset_description', 'dataset_id', 'dataset_name', 'dataset_version_id', 'dv_id', 'dv_name', 'dv_user_email', 'dv_user_id', 'dv_username', 'filename', 'filesize', ]
NON_SHAPEFILE_SET_PARAMS = [ 'datafile_download_url', 'filename', 'filesize']

def get_shapefile_from_dv_api_info(dv_session_token, shp_dict):
    """Using Dataverse API information, create a :model:`gis_shapefiles.ShapefileSet' object.  This function should only receive successful responses.
    
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
    
    # Check for existing shapefile sets based on the kwargs
    existing_sets = ShapefileSet.objects.filter(**shp_dict\
                                ).values_list('md5', flat=True\
                                ).order_by('created')

    existing_sets = list(existing_sets)
    
    # Existing ShapefileSet(s) found
    # Return the md5, delete other groups, if any
    if len(existing_sets) > 0:
        shp_md5 = existing_sets.pop()
        if len(existing_sets) > 0:
            ShapefileSet.objects.filter(md5__in=existing_sets).delete()   # delete older ShapefileSet(s)
        return shp_md5

    #------------------------------
    # Make a new group
    #------------------------------
    if dv_session_token:
        shp_dict['dv_session_token'] = dv_session_token
    shapefile_set = ShapefileSet(**shp_dict)
    shapefile_set.save()
    
    # Download and attach file
    img_temp = NamedTemporaryFile(delete=True)
    img_temp.write(urllib2.urlopen(datafile_download_url).read())
    img_temp.flush()

    shapefile_set.dv_file.save(datafile_filename, File(img_temp))
    shapefile_set.save()           
    
    return shapefile_set.md5      
   
'''

def update_shapefileset_with_metadata(shp_info_obj):
    """
    Remember to close the .zip via the ShapefileZipCheck object!
    """
    if shp_info_obj is None:
        return
        
    zip_checker = ShapefileZipCheck(shp_info_obj.dv_file, **{'is_django_file_field': True})
    #zip_checker = ShapefileZipCheck(os.path.join(MEDIA_ROOT, shp_info.shp_file.name))
    zip_checker.validate()
    
    #-------------------------------------
    # (1) No shapefiles found in .zip
    #-------------------------------------
    list_of_shapefile_set_names = zip_checker.get_shapefile_setnames()
    if list_of_shapefile_set_names is None:
        zip_checker.close_zip()        
        shp_info_obj.has_shapefile = False
        shp_info_obj.save()
        return
    
    #-------------------------------------
    # (2) Add basic data (later; add file sizes, etc)
    #-------------------------------------
    shp_info_obj.has_shapefile = True
    shp_info_obj.shapefile_names = json.dumps(list_of_shapefile_set_names)
    shp_info_obj.num_shapefiles = len(list_of_shapefile_set_names)    
    shp_info_obj.save()

    #-------------------------------------
    # (3) If only 1 shapefile, then get shapefile info
    #-------------------------------------
    if shp_info_obj.num_shapefiles == 1:
       if zip_checker.load_shapefile(shp_info_obj, list_of_shapefile_set_names[0]):
           try:
               sr = shapefile.Reader(shp_info_obj.extracted_shapefile_load_path)
           except:
               if shp_info_obj:
                   logger.error('Failed to read shapefile from extracted path: %s\nShapefileGroup id:%s' %\
                        (extracted_shapefile_load_path, shp_info_obj.id)\
                        )
               else:
                   logger.error('ShapefileGroup is None! Failed to read shapefile from extracted path: %s' %\
                        (extracted_shapefile_load_path)\
                        )
                   
               return
       
              
       # update_with_single_shapefile_info(shp_info_obj, list_of_shapefile_set_names[0] )
       #ZipFile.read
        
       return
        
    #-------------------------------------
    # (4) Multiple shapefiles, let the user choose one
    #-------------------------------------
    zip_checker.close_zip()        
    
        
'''        
def update_with_single_shapefile_info(shp_info_obj, shapefile_base_name):
    """
    Need to extract files from .zip!    
    """
    print 'blah'
    if shp_info_obj is None or shapefile_base_name is None:
        return
        
    #myshp = open(os.path.join(config.BOSTON_SHAPEFILES, "income_in_boston_gui.shp"), "rb")
    #mydbf = open(os.path.join(config.BOSTON_SHAPEFILES, "income_in_boston_gui.dbf"), "rb")
    #myshx = open(os.path.join(config.BOSTON_SHAPEFILES, "income_in_boston_gui.shx"), "rb")
        #mydbf = open("shapefiles/blockgroups.dbf", "rb")
        
    #sf_reader = shapefile.Reader(shp_info_obj.shp_file)
