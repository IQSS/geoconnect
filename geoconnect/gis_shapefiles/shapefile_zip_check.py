import os, sys
import shapefile
import zipfile
import timeit
import cStringIO

from gis_shapefiles.models import ShapefileSet, SingleFileInfo, SHAPEFILE_MANDATORY_EXTENSIONS, WORLDMAP_MANDATORY_IMPORT_EXTENSIONS 

import logging
#logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)

"""
import zipfile

import urllib, zipfile, cStringIO
zipwebfile = urllib.urlopen('http://downloads.egenix.com/python/locale-0.1.zip')
buffer = cStringIO.StringIO(zipwebfile.read())
zfile = zipfile.ZipFile(buffer, 'r')
zfile.printdir()

z = zipfile.ZipFile(fh, mode="r", compression=ZIP_STORED, allowZip64=True) 
z = zipfile.ZipFile(fh, mode="r", compression=zipfile.ZIP_STORED, allowZip64=True) 

"""
class ZipToStringIOConverter:
    
    @staticmethod
    def from_django_file_field(django_field_file_obj):
        """Given a Django FieldFile object, return a cStringIO.StringIO with the contents of the related file
            ff_obj  FieldFile object with a pointer to a valid file
        """
        if django_field_file_obj is None:
            print 'django_field_file_obj is None'
            return None
            
        if not django_field_file_obj.__class__.__name__ == 'FieldFile':
            print 'class name: ', django_field_file_obj.__class__.__name__            
            return None
    
        return cStringIO.StringIO(django_field_file_obj.read())

    
class ShapefileZipCheck:
    """Check to see if a file or buffer (StringIO) is a valid zipefile that contains at least one shapefile set
    
    """
    def __init__(self, zip_input, **kwargs):
        """
        Inspect a .zip archive  to see if it contains one or more shapefile sets.  
        
        Attributes:
            zip_input   full path to a file, StringIO object, url to a .zip, or Django file field
                Set kwargs depending on input: 
                    - file, no kwargs needed
                    - StringIO, no kwargs needed
                    - url to a .zip, {  'is_url_to_zip' : True }
                    - django file field, {  'is_django_file_field' : True }                    

            potential_shapefile_sets    dict with shapefile basename key + individual files
                example: { 'CommunityCenters_Pag': [u'CommunityCenters_Pag.shx', u'CommunityCenters_Pag.cst', u'CommunityCenters_Pag.dbf', u'CommunityCenters_Pag.prj', u'CommunityCenters_Pag.shp']}
            err_detected  boolean, is there a processing error?
            err_msg details regarding the error
        """       
        self.err_detected = False
        self.err_msg = ''
        self.zip_obj = None
        
        if kwargs.get('is_url_to_zip') is True:
            print 'NEED TO IMPLMENT URL ZIPFILE'
            # Do nothing for now
            self.zip_input = zip_input
        elif kwargs.get('is_django_file_field') is True:
            #print 'is_django_file_field'
            self.zip_input = ZipToStringIOConverter.from_django_file_field(zip_input)
            if self.zip_input is None:
                self.err_detected = True
                self.err_msg = 'Failed to find data in Django FileField'
                raise Exception('Failed to find data in Django FileField')
        else:
            self.zip_input = zip_input
        
        self.potential_shapefile_sets = {}
    

    def has_potential_shapefiles(self):
        if len(self.potential_shapefile_sets) == 0:
            return False
        return True
        
    def get_shapefile_setnames(self):
        """
        Return the unique basenames of the potential shapefile sets
            Example: if dict self.potential_shapefile_sets is { 'CommunityCenters_Pag': [u'CommunityCenters_Pag.shx', u'CommunityCenters_Pag.cst', u'CommunityCenters_Pag.dbf', u'CommunityCenters_Pag.prj', u'CommunityCenters_Pag.shp']}
                    return ['CommunityCenters_Pag']
        """
        if len(self.potential_shapefile_sets) == 0:
            return None
    
        # Case not checked!  Same shapefile basename in different directories
        l = self.potential_shapefile_sets.keys()
        #l = [ os.path.basename(x) for x in l]
        return l
    
    def close_zip(self):
        if self.zip_obj is None:
            return
        
        try:
            self.zip_obj.close()
        except:
            # log something!!
            return
    
    def load_shapefile_from_open_zip(self, shapefile_basename, shapefile_set):
        """
        Assumes that self.zip_obj has opened an archive that contains a valid shapefile set
        
        param: shapefile_basename: Name of shapefile basename to remove from .zip.  
            Will be stripped of any preceding directory "foo/bar" becomes "bar"
        type: shapefile_basename: str 
        """
        if self.zip_obj is None:
            msg = 'The shapefile was not open'
            logger.error(msg)            
            return (False, msg)

        if shapefile_basename is None:      # no shapefile_basename specified, use name in self.potential_shapefile_sets                
            msg = 'The shapefile name was not specified'
            logger.error(msg)            
            return (False, msg)
        
        if shapefile_set is None:      # no shapefile_basename specified, use name in self.potential_shapefile_sets                
            msg = 'The ShapefileSet was not specified'
            logger.error(msg)            
            return (False, msg)

        shapefile_basename = os.path.basename(shapefile_basename)
        logger.info('shapefile_basename: %s' % shapefile_basename)

        for archived_filename in self.potential_shapefile_sets.keys():            
            if shapefile_basename == os.path.basename(archived_filename):
                name_found = True
                name_to_extract = archived_filename
                break

        if not name_found:
            msg = 'shapefile_basename not found in .zip: %s' % shapefile_basename
            logger.error(msg)            
            return (False, msg)
        
        # #------------------------
        shapefile_set.name = shapefile_basename
        shapefile_set.save()

        for ext in WORLDMAP_MANDATORY_IMPORT_EXTENSIONS:
            fname = name_to_extract + ext
            logger.info('extracting: %s' % fname)
            self.zip_obj.extract(fname, shapefile_set.get_scratch_work_directory())
            logger.info('extracted: %s' % fname)
            sfi = SingleFileInfo(name=os.path.basename(fname)\
                                , shapefile_set=shapefile_set\
                                , extension=ext\
                                , filesize=0\
                                , is_required_shapefile=True\
                                , extracted_file_path=os.path.join(shapefile_set.get_scratch_work_directory(), fname)\
                                )
            sfi.save()

        extracted_shapefile_load_path = os.path.join(shapefile_set.get_scratch_work_directory(), name_to_extract)
        shapefile_set.extracted_shapefile_load_path = extracted_shapefile_load_path

        # let it blow up for now
        shp_reader = shapefile.Reader(extracted_shapefile_load_path + '.shp')
        #try:
        #    shp_reader = shapefile.Reader(extracted_shapefile_load_path)
        #except shapefile.ShapefileException:
        #    msg = 'Error opening shapefile: %s' % extracted_shapefile_load_path
        #    logger.error(msg)            
        #    return (False, msg)
            
        # add number of shapes
        shapefile_set.number_of_features = len(shp_reader.shapes())

        # add column names
        shapefile_set.add_column_info(shp_reader.fields[1:])   
        shapefile_set.add_column_names_using_fields(shp_reader.fields)

        # add bounding box
        print 'add bounding box', shp_reader.bbox

        try:
            shapefile_set.add_bounding_box(list(shp_reader.bbox))
        except:
            shapefile_set.add_bounding_box('')

        shapefile_set.save()

        logger.info('ShapefileSet updated!')

        return (True, None)
        #------------------------
        
    def load_shapefile(self, shp_group_obj, shapefile_basename):
        """
        shp_group_obj    ShapefileGroup object

        shapefile_basename     Name of shapefile basename to remove from .zip; 
                                Will be stripped of any preceding directory "foo/bar" becomes "bar"

        Load a shapefile and extract metadata:
            - column names
            - number of objects
        """
        if self.zip_obj is None or shp_group_obj is None or shapefile_basename is None:
            msg = 'load_shapefile(...) failed.  One of these was None: self.zip_obj, shp_group_obj, shapefile_basename'
            logger.error(msg)            
            return (False, msg)
        
        shapefile_basename = os.path.basename(shapefile_basename)
        logger.info('shapefile_basename: %s' % shapefile_basename)

        """
        Check the case where the "shapefile_basename" is not the full name in the zipfile
            e.g. User may pick :
                    "income_in_boston"
                But .zip archive has:
                    "some_dir/income_in_boston"
        """
        name_found = False
        logger.info('Checking .zip file list for basename: %s' % shapefile_basename)
        for archived_filename in self.potential_shapefile_sets.keys():
            
            if shapefile_basename == os.path.basename(archived_filename):
                name_found = True
                name_to_extract = archived_filename
                break

        if not name_found:
            msg = 'shapefile_basename not found in .zip: %s' % shapefile_basename
            logger.error(msg)            
            return (False, msg)
            
        single_shapefile_set = ShapefileSet(name=name_to_extract\
                                            , shapefile_group=shp_group_obj\
                                            )    
        single_shapefile_set.save()
        
        for ext in WORLDMAP_MANDATORY_IMPORT_EXTENSIONS:
            fname = name_to_extract + ext
            logger.info('extracting: %s' % fname)
            self.zip_obj.extract(fname, shp_group_obj.get_scratch_work_directory())
            logger.info('extracted: %s' % fname)
            sfi = SingleFileInfo(name=os.path.basename(fname)\
                                , shapefile_set=single_shapefile_set\
                                , extension=ext\
                                , filesize=0\
                                , is_required_shapefile=True\
                                , extracted_file_path=os.path.join(shp_group_obj.get_scratch_work_directory(), fname)\
                                )
            sfi.save()
            
        extracted_shapefile_load_path = os.path.join(shp_group_obj.get_scratch_work_directory(), name_to_extract)
        single_shapefile_set.extracted_shapefile_load_path = extracted_shapefile_load_path
        
        shp_reader = shapefile.Reader(extracted_shapefile_load_path)
        
        # add number of shapes
        single_shapefile_set.number_of_features = len(shp_reader.shapes())
        
        # add column names
        single_shapefile_set.add_column_info(shp_reader.fields[1:])   
        single_shapefile_set.add_column_names_using_fields(shp_reader.fields)

        # add bounding box
        print 'add bounding box', shp_reader.bbox
        
        try:
            single_shapefile_set.add_bounding_box(list(shp_reader.bbox))
        except:
            single_shapefile_set.add_bounding_box('')
        
        single_shapefile_set.save()

        logger.info('new ShapefileSet saved')
        
        return (True, single_shapefile_set)
        
    
    def get_zipfile_names(self):
        if self.zip_obj is None:
            return None
        namelist = [z for z in self.zip_obj.namelist() if not z[:2] == '__']
        return namelist
        
    def validate(self):
        """Does this .zip contain at least 1 valid shapefile set?
        - Is this a zipfile?
        - Iterate through file listings to find potential shapefile sets (potential_shapefile_sets) based on filename extensions?

        returns True or False and sets the dict self.potential_shapefile_sets
        """
                 
        # Is it a file?
        if not os.path.isfile(self.zip_input):
            self.err_detected = True
            self.err_msg = 'File not found for zip_input: %s' % self.zip_input
            logger.debug(self.err_msg )
            return False

        # Is it a zip file?
        if not zipfile.is_zipfile(self.zip_input):
            self.err_detected = True
            self.err_msg = 'Not a zip archive'
            logger.debug(self.err_msg )
            return False

        self.zip_obj = zipfile.ZipFile(self.zip_input, 'r')
        
        #for l in z.infolist(): l.name,l.filename, l.date_time
        
        zip_info_list = self.zip_obj.infolist()
        logger.debug('zip_info_list: %s' % zip_info_list)            
        
        zip_info_list = [z for z in zip_info_list if not z.filename[:2] == '__']
        
        # Create file groups to shake for needed shape files
        file_groups = {}

        # Iterate through filenames.
        # Make a dict with basename and a list of extensions.  
        # Ignore files without extensions.
        #    
        #   e.g.  { 'Tracts' : [ '.dbf', '.prj', '.sbn', '.sbx', '.shp', '.shx'] 
        #            , 'my_word_doc' : ['.docx'] 
        #
        for zip_info in zip_info_list:
            n = zip_info.filename
            if not len(n) >= 5 and n[-4]=='.':      # Does this name have a file extension ".xxx"
                pass
            file_groups.setdefault(n[:-4], []).append(n[-4:])    

        
        #
        #   Check dict to for potential shapefile sets
        #       e.g. extension_list = ['.DBF', 'sHp', 'docx', etc]
        #           .DBF -> checked as .dbf -> YES
        #           .sHp -> checked as .shp -> YES
        #           .docx -> checked as .docx -> NO
        #
        shapefile_groups = []
        for k, extension_list in file_groups.iteritems():
            if all(ext.lower() in extension_list for ext in WORLDMAP_MANDATORY_IMPORT_EXTENSIONS):
                shape_file_fnames = [ '%s%s' % (k, ext) for ext in extension_list ]
                self.potential_shapefile_sets.update({ k : shape_file_fnames})


        if len(self.potential_shapefile_sets) > 0:
            return True
        
        return False
           
    

if __name__ == '__main__':
    #fname = None
    #fname = '/Users/rmp553/Google Drive/BARI/test_data/boston-geo-infrastructure/Base Layers.zip'
    fname = '/Users/rmp553/Documents/iqss-git/geo-annotate/geoconnect/test_shapefiles/CommunityCenters_Pag.zip'
    
    ztest = ShapefileZipCheck(fname)
    #ztest = ShapefileZipCheck()
    ztest.validate()
    #print(timeit.timeit("ShapefileZipCheck(fname)", setup="from __main__ import ShapefileZipCheck, fname", number=10))
    
