import os
from os.path import isdir, isfile
import shutil
import shapefile
import zipfile
import cStringIO

from gc_apps.geo_utils.msg_util import msg, msgt
from gc_apps.gis_shapefiles.models import WORLDMAP_MANDATORY_IMPORT_EXTENSIONS, SHAPEFILE_EXTENSION_SHP
from gc_apps.geo_utils.template_constants import ZIPCHECK_NO_SHAPEFILES_FOUND,\
        ZIPCHECK_MULTIPLE_SHAPEFILES,\
        ZIPCHECK_NO_FILE_TO_CHECK,\
        ZIPCHECK_FAILED_TO_PROCCESS_SHAPEFILE

import logging
LOGGER = logging.getLogger(__name__)

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
class ZipToStringIOConverter(object):

    @staticmethod
    def from_django_file_field(django_field_file_obj):
        """Given a Django FieldFile object, return a cStringIO.StringIO with the contents of the related file
            ff_obj  FieldFile object with a pointer to a valid file
        """
        if django_field_file_obj is None:
            LOGGER.error('django_field_file_obj is None')
            return None

        if not django_field_file_obj.__class__.__name__ == 'FieldFile':
            LOGGER.debug('class name: %s', django_field_file_obj.__class__.__name__)
            return None

        #return django_field_file_obj.read()

        return cStringIO.StringIO(django_field_file_obj.read())


class ShapefileZipCheck(object):
    """
    Check to see if a file or buffer (StringIO) is a valid zipefile
    that contains at least one shapefile set
    """

    ERR_MSG_NOT_ZIP_ARCHIVE = 'Not a zip archive'
    ERR_MSG_NO_SHAPEFILES_IN_ZIP_ARCHIVE = 'No shapefiles found in this .zip file'
    ERR_MULTIPLE_SHAPEFILES_IN_ZIP_ARCHIVE = 'Multiple shapefiles were in this .zip file'

    def __init__(self, zip_input, **kwargs):
        """
        Inspect a .zip archive  to see if it contains a single shapefile set.

        From the embedded ".shp" file, retrieve the number of features and column names

        Attributes:
            zip_input   full path to a file, StringIO object, url to a .zip, or Django file field
                Set kwargs depending on input:
                    - file, no kwargs needed
                    - StringIO, no kwargs needed
                    - url to a .zip, {  'is_url_to_zip' : True }
                    - django file field, {  'is_django_file_field' : True }

            potential_shapefile_sets    dict with shapefile basename key + individual files
                example: { 'CommunityCenters_Pag': [u'CommunityCenters_Pag.shx', u'CommunityCenters_Pag.cst', u'CommunityCenters_Pag.dbf', u'CommunityCenters_Pag.prj', u'CommunityCenters_Pag.shp']}
            has_err  boolean, is there a processing error?
            err_msg details regarding the error
        """

        # Potential Error flags
        self.has_err = False   # Always True on an error
        self.error_msg = ''
        self.error_type = None

        self.err_no_shapefiles = False
        self.err_multiple_shapefiles = False
        self.err_no_file_to_check = False
        self.err_could_not_process_shapefile = False

        # Err msg

        # zip object
        self.zip_obj = None

        self.potential_shapefile_sets = {}

        self.zip_input = zip_input

        self.run_initial_check(**kwargs)

    def run_initial_check(self, **kwargs):

        if self.zip_input is None:
            self.add_error(None, ZIPCHECK_NO_FILE_TO_CHECK)
            return False

        if kwargs.get('is_url_to_zip') is True:
            raise Exception('Have not implemented getting a .zip from a url')

        elif kwargs.get('is_django_file_field') is True:
            #print 'is_django_file_field'
            self.zip_input = ZipToStringIOConverter.from_django_file_field(self.zip_input)
            if self.zip_input is None:
                err_msg = 'Failed to find data in Django FileField'
                self.add_error(err_msg)
                raise Exception(err_msg)    # Just blow up if this happens
            else:
                pass
                #msgt("Loaded from AWS!")
        return True

    def add_error(self, err_msg, err_type=None):
        """Store errors internal to this class"""

        self.has_err = True
        self.error_msg = err_msg
        self.error_type = err_type


    def has_potential_shapefiles(self):
        """Convenience method for checking for shapefile sets"""
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


    def load_shapefile_from_open_zip(self, shapefile_basename, shapefile_info):
        """
        Assumes that self.zip_obj has opened an archive that contains a valid shapefile set

        param: shapefile_basename: Name of shapefile basename to remove from .zip.
            Will be stripped of any preceding directory "foo/bar" becomes "bar"
        type: shapefile_basename: str
        """
        if self.has_err:
            return False

        if self.zip_obj is None:
            self.add_error('The shapefile was not open')
            return False

        if shapefile_basename is None:
            self.add_error('The shapefile name was not specified')
            return False

        if shapefile_info is None:
            self.add_error('The ShapefileInfo was not specified')
            return False

        shapefile_basename = os.path.basename(shapefile_basename)
        LOGGER.info('shapefile_basename: %s', shapefile_basename)

        # ------------------------------------
        #    Go through keys to match basename.  In this case, may
        #       be looking for 'bicycles':
        #
        #     { 'bicycles' : [ '.dbf', '.prj', '.sbn', '.sbx', '.shp', '.shx'],
        #       'my_word_doc' : ['.docx'],
        #       'README' : ['.md']
        #      }
        # ------------------------------------
        name_found = False
        name_to_extract = None
        for archived_filename in self.potential_shapefile_sets.keys():
            if shapefile_basename == os.path.basename(archived_filename):
                name_found = True
                name_to_extract = archived_filename # includes path info
                break

        if not name_found:
            err_msg = 'shapefile_basename not found in .zip: %s' % shapefile_basename
            self.add_error(err_msg)
            return False

        # ------------------------------------
        # Update shapefilename using the basename
        # ------------------------------------
        shapefile_info.name = shapefile_basename
        shapefile_info.save()

        # ------------------------------------
        # Extract the zipped file into a scratch directory
        #   - Only extract the 4 files necessary for WorldMap
        # ------------------------------------
        scratch_directory = shapefile_info.get_scratch_work_directory()
        for shp_ext in WORLDMAP_MANDATORY_IMPORT_EXTENSIONS:
            shp_part_name = name_to_extract + shp_ext

            # Extract the file to a scratch directory
            zip_part_path = self.zip_obj.extract(shp_part_name, scratch_directory)

        # ------------------------------------
        # Can we read the '.shp' file?
        # ------------------------------------
        extracted_shapefile_load_path = os.path.join(scratch_directory, name_to_extract)
        shapefile_info.extracted_shapefile_load_path = extracted_shapefile_load_path

        full_shp_fname = extracted_shapefile_load_path + SHAPEFILE_EXTENSION_SHP
        if not isfile(full_shp_fname):
            self.add_error(".shp file not found! Tried: %s" % full_shp_fname)
            return False

        # ------------------------------------
        # Try to process/pull info from the .shp file
        # ------------------------------------
        try:
            shp_reader = shapefile.Reader(full_shp_fname)
        except:
            err_msg = 'Shapefile reader failed for file: %s' % (full_shp_fname)
            self.add_error(err_msg, ZIPCHECK_FAILED_TO_PROCCESS_SHAPEFILE)
            return False


        # ------------------------------------
        # Extract feature count, column names, bounding box
        # ------------------------------------
        shapefile_info.number_of_features = len(shp_reader.shapes())
        if shapefile_info.number_of_features == 0:
            err_msg = "This shapefile does not have any geospatial features"
            self.add_error(err_msg, ZIPCHECK_FAILED_TO_PROCCESS_SHAPEFILE)
            return False

        # add column names
        # -----------------
        shapefile_info.add_column_info(shp_reader.fields[1:])
        shapefile_info.add_column_names_using_fields(shp_reader.fields)

        # add bounding box
        # -----------------
        try:
            shapefile_info.add_bounding_box(list(shp_reader.bbox))
        except:
            shapefile_info.add_bounding_box('')

        # ----------------------
        # Remove the scratch directory
        # ----------------------
        shp_reader = None
        if isdir(scratch_directory):
            shutil.rmtree(scratch_directory)
            shapefile_info.extracted_shapefile_load_path = ''

        # ----------------------
        # Save the metadata!!
        # ----------------------
        shapefile_info.save()

        return True


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
        if self.has_err:
            return False

        # ---------------------------
        # Is it a file?
        # ---------------------------
        #if not isfile(self.zip_input):
        #    self.add_error('File not found for zip_input: %s' % self.zip_input)
        #    return False

        # ---------------------------
        # Is it a zip file?
        # ---------------------------
        if not zipfile.is_zipfile(self.zip_input):
            self.add_error(ShapefileZipCheck.ERR_MSG_NOT_ZIP_ARCHIVE,\
                    ZIPCHECK_NO_SHAPEFILES_FOUND)
            return False

        # ---------------------------
        # Examine the zip file contents
        # ---------------------------
        self.zip_obj = zipfile.ZipFile(self.zip_input, 'r')

        # Get the file list
        #
        zip_info_list = self.zip_obj.infolist()

        #  Remove names starting with "__"
        #
        zip_info_list = [z for z in zip_info_list if not z.filename[:2] == '__']

        # Create file groups to check for needed shape files
        #
        file_groups = {}

        # Iterate through filenames.
        # Make a dict with basename and a list of extensions.
        # Ignore files without extensions.
        #
        #   e.g.  { 'Tracts' : [ '.dbf', '.prj', '.sbn', '.sbx', '.shp', '.shx']
        #            , 'my_word_doc' : ['.docx']
        #
        for zip_info in zip_info_list:
            entry_name = zip_info.filename

            # Make sure file name is at least 5 chars and
            #   has a "." as 4th char from the right
            # Does this name have a file extension ".xxx"
            if len(entry_name) >= 5 and entry_name[-4] == '.':
                file_groups.setdefault(entry_name[:-4], []).append(entry_name[-4:])


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
                shape_file_fnames = ['%s%s' % (k, ext) for ext in extension_list]
                self.potential_shapefile_sets.update({k : shape_file_fnames})


        if len(self.potential_shapefile_sets) == 0:     # No shapefiles found
            self.add_error(ShapefileZipCheck.ERR_MSG_NO_SHAPEFILES_IN_ZIP_ARCHIVE,\
                ZIPCHECK_NO_SHAPEFILES_FOUND)
            return False

        elif len(self.potential_shapefile_sets) > 1:    # Multiple shapefiles found
            self.add_error(ShapefileZipCheck.ERR_MULTIPLE_SHAPEFILES_IN_ZIP_ARCHIVE,\
                            ZIPCHECK_MULTIPLE_SHAPEFILES)
            return False

        # Only 1 shapefile found
        #
        return True



if __name__ == '__main__':
    #fname = None
    #fname = '/Users/rmp553/Google Drive/BARI/test_data/boston-geo-infrastructure/Base Layers.zip'
    fname = '/Users/rmp553/Documents/iqss-git/geo-annotate/geoconnect/test_shapefiles/CommunityCenters_Pag.zip'

    ztest = ShapefileZipCheck(fname)
    #ztest = ShapefileZipCheck()
    ztest.validate()
    #print(timeit.timeit("ShapefileZipCheck(fname)", setup="from __main__ import ShapefileZipCheck, fname", number=10))
