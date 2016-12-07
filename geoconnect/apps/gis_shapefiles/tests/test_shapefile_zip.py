from os.path import abspath, dirname, isfile, join, isdir

import unittest
import json

from django.test import TestCase
from django.conf import settings

from geo_utils.msg_util import *
from apps.gis_shapefiles.shapefile_zip_check import ShapefileZipCheck
from apps.gis_shapefiles.models import ShapefileInfo

from geo_utils.template_constants import ZIPCHECK_NO_SHAPEFILES_FOUND,\
        ZIPCHECK_MULTIPLE_SHAPEFILES,\
        ZIPCHECK_NO_FILE_TO_CHECK,\
        ZIPCHECK_FAILED_TO_PROCCESS_SHAPEFILE

# python manage.py test apps.gis_shapefiles.tests
#

class ShapefileBasicTests(TestCase):
    #fixtures = ['polls_forms_testdata.json']

    def get_shp_params(self):
        test_data_file = join( dirname(dirname(abspath(__file__)))\
                                    , 'fixtures'\
                                    , 'dataverse_info_test_fixtures_01.json'\
                                )
        if not isfile(test_data_file):
                raise ValueError('File not found: %s' % test_data_file)

        return json.loads(open(test_data_file, 'r').read())


    def setUp(self):
        self.test_files_dirname = join(settings.PROJECT_TEST_FILES_DIR, 'shapefiles')
        if not isdir(self.test_files_dirname):
            raise IOError('Test directory not found: %s' % self.test_files_dirname)

        shp_params = self.get_shp_params()
        self.shp_set = ShapefileInfo(**shp_params)
        # ['datafile_id', 'datafile_label', 'dv_user_email', 'dv_user_id', 'dv_username', 'dv_file']


    def get_test_file(self, fname):
        fullpath = join(self.test_files_dirname, fname)
        if not isfile(fullpath):
            raise IOError('Test file not found: %s' % fullpath)
        return fullpath

    #@unittest.skip("skipping test_01_shapefile_check_bad_files")
    def test_01_shapefile_check_bad_files(self):
        """test_01_shapefile_check_bad_files"""
        msgt(self.test_01_shapefile_check_bad_files.__doc__)


        msg('Test 01: Pass None, raise an exception in constructor')
        zip_checker = ShapefileZipCheck(None)
        self.assertEqual(zip_checker.has_err, True)
        self.assertEqual(zip_checker.error_type, ZIPCHECK_NO_FILE_TO_CHECK)
        zip_checker.validate()
        self.assertEqual(zip_checker.has_err, True)
        self.assertEqual(zip_checker.error_type, ZIPCHECK_NO_FILE_TO_CHECK)


        msgd('Test 01a: Text file, not a zip')
        zip_checker = ShapefileZipCheck(self.get_test_file('t-01-not-a-zip.txt'))
        zip_checker.validate()
        self.assertEqual(zip_checker.has_err, True)
        self.assertEqual(zip_checker.error_msg, ShapefileZipCheck.ERR_MSG_NOT_ZIP_ARCHIVE)


        msgd('Test 02: Text file, .zip extension but not a .zip')
        zip_checker = ShapefileZipCheck(self.get_test_file('t-02-not-a-zip-bad-ext.zip'))
        zip_checker.validate()
        self.assertEqual(zip_checker.has_err, True)
        self.assertEqual(zip_checker.error_msg, ShapefileZipCheck.ERR_MSG_NOT_ZIP_ARCHIVE)
        #msg(zip_checker.error_msg)


        msgd('Test 03: .zip file but not a zipped shapefile')
        zip_checker = ShapefileZipCheck(self.get_test_file('t-03-zip-but-not-shp.zip'))
        zip_checker.validate()
        self.assertEqual(zip_checker.has_err, True)
        self.assertEqual(zip_checker.error_msg, ShapefileZipCheck.ERR_MSG_NO_SHAPEFILES_IN_ZIP_ARCHIVE)
        #msg(zip_checker.error_msg)


        msgd('Test 03a: .zip file but 2 shapefiles detected')
        zip_checker = ShapefileZipCheck(self.get_test_file('t-03a-2shapes.zip'))
        zip_checker.validate()
        self.assertEqual(zip_checker.has_err, True)
        self.assertEqual(zip_checker.error_msg, ShapefileZipCheck.ERR_MULTIPLE_SHAPEFILES_IN_ZIP_ARCHIVE)
        #msg(zip_checker.error_msg)


        msgd('Test 04: zipped shapefile extensions but invalid')
        zip_checker = ShapefileZipCheck(self.get_test_file('t-04-right-extensions-but-zeroK-files.zip'))
        zip_checker.validate()

        msg('No error  yet, b/c files not loaded to shp library')
        # No error yet, b/c file
        self.assertEqual(zip_checker.has_err, False)
        self.assertEqual(zip_checker.has_potential_shapefiles(), True)

        msg(zip_checker.get_shapefile_setnames())
        self.assertEqual(zip_checker.get_shapefile_setnames(), ['buses'])

        was_success = zip_checker.load_shapefile_from_open_zip('buses', self.shp_set)
        self.assertEqual(was_success, False)
        self.assertEqual(zip_checker.error_msg.startswith('Shapefile reader failed for file'), True)

        #get_shapefile_setnames
        #self.assertEqual(zip_checker.error_msg, ShapefileZipCheck.ERR_MSG_NO_SHAPEFILES_IN_ZIP_ARCHIVE)
        #msg(zip_checker.error_msg)

    #@unittest.skip("skip test_shapefile_good_file")
    def test_02_shapefile_good_file(self):
        """test_02_shapefile_good_file"""
        msgt(self.test_02_shapefile_good_file.__doc__)

        msgd('Test 01: Good shapefile')
        zip_checker = ShapefileZipCheck(self.get_test_file('t-05-good-shp-social_disorder_in_boston.zip'))
        zip_checker.validate()

        # No error yet, b/c file
        self.assertEqual(zip_checker.has_err, False)
        self.assertEqual(zip_checker.has_potential_shapefiles(), True)
        self.assertEqual(zip_checker.get_shapefile_setnames()\
                    , ['social_disorder_in_boston/social_disorder_in_boston_yqh'])

        was_success = zip_checker.load_shapefile_from_open_zip('social_disorder_in_boston/social_disorder_in_boston_yqh', self.shp_set)

        #msg(msg_or_shp_object)
        self.assertEqual(was_success, True)

        msgd('Check column names')
        column_names = ['OBJECTID', 'AREA', 'PERIMETER', 'STATE', 'COUNTY', 'TRACT', 'BLOCKGROUP', 'BG_ID', 'CT_ID', 'BLK_COUNT', 'LOGRECNO', 'DRY_ACRES', 'DRY_SQMI', 'DRY_SQKM', 'SHAPE_AREA', 'SHAPE_LEN', 'HOODS_PD_I', 'Nbhd', 'NbhdCRM', 'NSA_ID', 'NSA_NAME', 'BG_ID_1', 'Homeowners', 'MedIncomeH', 'propwhite', 'propblack', 'propasian', 'prophisp', 'medage', 'propcolleg', 'TotalPop', 'popden', 'Type', 'ID2', 'BG_ID_12', 'SocDis_201', 'SocStrife_', 'Alcohol_20', 'Violence_2', 'Guns_2010', 'SocStrife1', 'SocDis_202', 'SocStrif_1', 'Alcohol_21', 'Violence_3', 'Guns_2011', 'SocStrif_2', 'SocDis_203', 'SocStrif_3', 'Alcohol_22', 'Violence_4', 'Guns_2012', 'SocStrif_4']

        self.assertEqual(self.shp_set.column_names, column_names)

        msgd('Check bounding box')
        bounding_box = [225470.00063935894, 886437.2096943911, 242303.560639359, 905485.1596943911]
        self.assertEqual(self.shp_set.bounding_box, bounding_box)

        msgd('Check feature count')
        self.assertEqual(self.shp_set.number_of_features, 544)
        #self.assertEqual(zip_checker.get_shapefile_setnames(), ['buses'])
