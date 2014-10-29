from os.path import join, isdir, isfile #, dirname, abspath

import unittest
import json

from os.path import abspath, dirname, isfile, join

from django.test import TestCase
from django.conf import settings

from geo_utils.msg_util import *
from apps.gis_shapefiles.shapefile_zip_check import ShapefileZipCheck
from apps.gis_shapefiles.models import ShapefileInfo

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

    #@unittest.skip("skipping")
    def test_shapefile_check_bad_files(self):
        msgt('ShapefileBasicTests.test_shapefile_check_bad_files')


        msg('Test 01: Pass None, raise an exception in constructor')
        zip_checker = ShapefileZipCheck(None)
        self.assertEqual(zip_checker.err_detected, True)
        self.assertEqual(zip_checker.err_no_file_to_check, True)
        zip_checker.validate()
        self.assertEqual(zip_checker.err_detected, True)
        self.assertEqual(zip_checker.err_no_file_to_check, True)


        #self.assertEqual(zip_checker.err_detected, True)
        #msg(zip_checker.err_msg)

        msgd('Test 01a: Text file, not a zip')
        zip_checker = ShapefileZipCheck(self.get_test_file('t-01-not-a-zip.txt'))
        zip_checker.validate()
        self.assertEqual(zip_checker.err_detected, True)
        self.assertEqual(zip_checker.err_msg, ShapefileZipCheck.ERR_MSG_NOT_ZIP_ARCHIVE)

        msgd('Test 02: Text file, .zip extension but not a .zip')
        zip_checker = ShapefileZipCheck(self.get_test_file('t-02-not-a-zip-bad-ext.zip'))
        zip_checker.validate()
        self.assertEqual(zip_checker.err_detected, True)
        self.assertEqual(zip_checker.err_msg, ShapefileZipCheck.ERR_MSG_NOT_ZIP_ARCHIVE)
        #msg(zip_checker.err_msg)

        msgd('Test 03: .zip file but not a zipped shapefile')
        zip_checker = ShapefileZipCheck(self.get_test_file('t-03-zip-but-not-shp.zip'))
        zip_checker.validate()
        self.assertEqual(zip_checker.err_detected, True)
        self.assertEqual(zip_checker.err_msg, ShapefileZipCheck.ERR_MSG_NO_SHAPEFILES_IN_ZIP_ARCHIVE)
        #msg(zip_checker.err_msg)

        msgd('Test 03a: .zip file but 2 shapefiles detected')
        zip_checker = ShapefileZipCheck(self.get_test_file('t-03a-2shapes.zip'))
        zip_checker.validate()
        self.assertEqual(zip_checker.err_detected, True)
        self.assertEqual(zip_checker.err_msg, ShapefileZipCheck.ERR_MULTIPLE_SHAPEFILES_IN_ZIP_ARCHIVE)
        #msg(zip_checker.err_msg)


        msgd('Test 04: zipped shapefile extensions but invalid')
        zip_checker = ShapefileZipCheck(self.get_test_file('t-04-right-extensions-but-zeroK-files.zip'))
        zip_checker.validate()
        msg('No error  yet, b/c files not loaded to shp library')
        # No error yet, b/c file
        self.assertEqual(zip_checker.err_detected, False)
        self.assertEqual(zip_checker.has_potential_shapefiles(), True)
        msg(zip_checker.get_shapefile_setnames())
        self.assertEqual(zip_checker.get_shapefile_setnames(), ['buses'])

        (success, msg_or_shp_object) = zip_checker.load_shapefile_from_open_zip('buses', self.shp_set)
        self.assertEqual(success, False)
        self.assertEqual(msg_or_shp_object.startswith('Shapefile reader failed for file'), True)
        
        #get_shapefile_setnames
        #self.assertEqual(zip_checker.err_msg, ShapefileZipCheck.ERR_MSG_NO_SHAPEFILES_IN_ZIP_ARCHIVE)
        #msg(zip_checker.err_msg)

    #@unittest.skip("skip test_shapefile_good_file")
    def test_shapefile_good_file(self):
        msgt('ShapefileBasicTests.test_shapefile_good_file')

        msgd('Test 01: Good shapefile')
        zip_checker = ShapefileZipCheck(self.get_test_file('t-05-good-shp-social_disorder_in_boston.zip'))
        zip_checker.validate()
        msg('Should be good')
        # No error yet, b/c file
        self.assertEqual(zip_checker.err_detected, False)
        self.assertEqual(zip_checker.has_potential_shapefiles(), True)
        self.assertEqual(zip_checker.get_shapefile_setnames()\
                    , ['social_disorder_in_boston/social_disorder_in_boston_yqh'])

        (success, msg_or_shp_object) = zip_checker.load_shapefile_from_open_zip('social_disorder_in_boston/social_disorder_in_boston_yqh', self.shp_set)
        msg(msg_or_shp_object)
        self.assertEqual(success, True)
        #msg(zip_checker.get_shapefile_setnames())
        #self.assertEqual(zip_checker.get_shapefile_setnames(), ['buses'])