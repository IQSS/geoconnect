import json
import urllib2

from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

from gis_shapefiles.shapefile_zip_check import ShapefileZipCheck
from gis_shapefiles.models import ShapefileGroup
import shapefile

import logging
logger = logging.getLogger(__name__)


def get_shapefile_group_md5_from_metadata(shp_dict):
    if shp_dict is None:
        return None
        
    req_keys = ['name', 'filename', 'dv_username', 'dataset_link']
    if not all(rkey in shp_dict.keys() for rkey in req_keys):
        raise Exception('Not all keys found in %s' % shp_dict)

    filename = shp_dict.get('filename')
    shp_dict.pop('filename')

    # Check for existing groups based on the kwargs
    existing_md5s = ShapefileGroup.objects.filter(**shp_dict\
                                ).values_list('md5', flat=True\
                                ).order_by('created')

    existing_md5s = list(existing_md5s)
    # Existing group(s) found
    # Return the md5, delete other groups, if any
    if len(existing_md5s) > 0:
        grp1_md5 = existing_md5s.pop()
        if len(existing_md5s) > 0:
            ShapefileGroups.objects.filter(md5__in=existing_md5s).delete()   # delete older groups
        return grp1_md5

    #------------------------------
    # Make a new group
    #------------------------------
    shape_group_obj = ShapefileGroup(**shp_dict)
    
    file_url = shp_dict['dataset_link']

    img_temp = NamedTemporaryFile(delete=True)
    img_temp.write(urllib2.urlopen(file_url).read())
    img_temp.flush()

    shape_group_obj.shp_file.save(filename, File(img_temp))
    shape_group_obj.save()           
    
    return shape_group_obj.md5      
    


def update_shapefileset_with_metadata(shp_info_obj):
    """
    Remember to close the .zip via the ShapefileZipCheck object!
    """
    if shp_info_obj is None:
        return
        
    zip_checker = ShapefileZipCheck(shp_info_obj.shp_file, **{'is_django_file_field': True})
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
