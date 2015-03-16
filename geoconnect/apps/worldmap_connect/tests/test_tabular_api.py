"""
Run tests for the WorldMap Tabular API

python manage.py test apps.worldmap_connect.tests.test_tabular_api.TestWorldMapTabularAPI
"""

import json
from os.path import realpath, dirname, isfile, join, isdir
import requests
from unittest import skip

from django.test import TestCase

# API path(s) are here
#
from shared_dataverse_information.worldmap_api_helper.url_helper import ADD_SHAPEFILE_API_PATH, DELETE_LAYER_API_PATH
from shared_dataverse_information.shapefile_import.forms import ShapefileImportDataForm
#from shared_dataverse_information.map_layer_metadata.forms import MapLayerMetadataValidationForm
from shared_dataverse_information.dataverse_info.forms_existing_layer import DataverseInfoValidationFormWithKey
from shared_dataverse_information.worldmap_datatables.forms import TableJoinResultForm
from shared_dataverse_information.map_layer_metadata.forms import WorldMapToGeoconnectMapLayerMetadataValidationForm

from shared_dataverse_information.worldmap_api_helper.url_helper import CLASSIFY_LAYER_API_PATH\
                , GET_LAYER_INFO_BY_DATAVERSE_INSTALLATION_AND_FILE_API_PATH\
                , GET_CLASSIFY_ATTRIBUTES_API_PATH

from apps.worldmap_connect.tests.tabular_test_helper import TabularTest

from geo_utils.msg_util import *



def setUpModule():
    msg( '---- Module setup ---- ')

def tearDownModule():
    msg( '---- Module teardown ---- ')


class TestWorldMapTabularAPI(TestCase):


    TEST_FILE_DIR = join(dirname(realpath(__file__)), 'input')
    existing_layer_name = None
    existing_layer_data = None
    layer_attribute_info = None
    #@classmethod
    #def setUpClass(cls):
    #    print "setUpClass"
    #    b = "Setup Class variable"

    @classmethod
    def tearDownClass(cls):
        msg('+++ tearDownClass +++')
        cls.delete_ma_tigerlines_shapefile()

    @classmethod
    def setUpClass(cls):
        msg('+++ setUpClass +++')
        #super(TestWorldMapTabularAPI, self).setUp()              #super().__init__(x,y)



        # Verify/load MA tigerlines test info
        #
        tab_ma_dataverse_info_fname = join(cls.TEST_FILE_DIR, 'tab_ma_dv_info.json')
        assert isfile(tab_ma_dataverse_info_fname), "MA tigerlines test fixture file not found: %s" % tab_ma_dataverse_info_fname
        cls.tab_ma_dv_info = json.loads(open(tab_ma_dataverse_info_fname, 'r').read())


        # Verify/load shapefile test info
        #
        tab_ma_shp_upload_request_fname = join(cls.TEST_FILE_DIR, 'tab_ma_shp_upload_request.json')
        assert isfile(tab_ma_shp_upload_request_fname), "Shapefile test fixture file not found: %s" % tab_ma_shp_upload_request_fname
        cls.tab_ma_shp_upload_request = json.loads(open(tab_ma_shp_upload_request_fname, 'r').read())

        # Verify that test shapefile exists (good file)
        #
        cls.tab_shp_ma_tigerlines_fname = join(cls.TEST_FILE_DIR, 'tab_shp_ma_tigerlines.zip')
        assert isfile(cls.tab_shp_ma_tigerlines_fname), "Test shapefile not found: %s" % self.tab_shp_ma_tigerlines_fname

        cls.existing_layer_name = 'boohoo'
        cls.existing_layer_data = 'boohoo existing_layer_data'
        cls.layer_attribute_info = 'boohoo layer_attribute_info'

        cls.upload_ma_tigerlines_shapefile()

    #def tearDown(self):
    #    msg('tearDown')    #cls.delete_ma_tigerlines_shapefile()


    @classmethod
    def upload_ma_tigerlines_shapefile(cls):

        #-----------------------------------------------------------
        msgt("--- SET UP:  Upload MA Tigerlines Shapefile ---")
        #-----------------------------------------------------------
        api_url = ADD_SHAPEFILE_API_PATH


        #-----------------------------------------------------------
        msgn("WorldMap shapefile import API -- with GOOD data/file")
        #-----------------------------------------------------------
        # Get basic shapefile info
        shapefile_api_form = ShapefileImportDataForm(cls.tab_ma_shp_upload_request)
        assert shapefile_api_form.is_valid(), "shapefile_api_form not valid: %s" % shapefile_api_form.errors


        test_shapefile_info = shapefile_api_form.get_api_params_with_signature()

        # add dv info
        test_shapefile_info.update(cls.tab_ma_dv_info)

        # prep file
        files = {'file': open( cls.tab_shp_ma_tigerlines_fname, 'rb')}

        #   Test WorldMap shapefile import API
        #
        msg('api url: %s' % api_url)
        r = requests.post(api_url\
                            , data=test_shapefile_info\
                            , files=files)

        try:
            r = requests.post(api_url\
                            , data=test_shapefile_info\
                            , files=files)
        except requests.exceptions.ConnectionError as e:
            msgx('Connection error: %s' % e.message)
        except:
            msgx("Unexpected error: %s" % sys.exc_info()[0])

        msg(r.status_code)
        msg('%s (truncated) ...' % r.text[:50])

        assert r.status_code==200, "Should receive 200 message.  Received: %s\n%s" % (r.status_code, r.text)

        try:
            rjson = r.json()
        except:
            assert False,  "Failed to convert response text to JSON. Text:\n%s" % r.text


        msgn("Get name of newly created layer")

        # Validate returned data
        f = WorldMapToGeoconnectMapLayerMetadataValidationForm(rjson.get('data', {}))
        assert f.is_valid(), 'Validation failed using WorldMapToGeoconnectMapLayerMetadataValidationForm. Errors: %s' % f.errors

        # Retrieve layer_name
        cls.existing_layer_data = rjson.get('data', {})
        cls.existing_layer_name = cls.existing_layer_data.get('layer_name', None)
        cls.layer_attribute_info = json.loads(cls.existing_layer_data.get('attribute_info', None))

        print 'cls.layer_attribute_info', cls.layer_attribute_info, cls.layer_attribute_info.__class__.__name__


        # Make sure layer_name is valid
        assert cls.existing_layer_name is not None, 'self.existing_layer_name cannot be None'
        assert len(cls.existing_layer_name) > 0, 'self.existing_layer_name cannot be length 0'


    @classmethod
    def delete_ma_tigerlines_shapefile(cls):
        #-----------------------------------------------------------
        msgt("--- TEAR DOWN: Delete MA Tigerlines Shapefile ---")
        #-----------------------------------------------------------

        api_prep_form = DataverseInfoValidationFormWithKey(cls.tab_ma_dv_info)
        assert api_prep_form.is_valid()\
                        , "Error.  Validation failed. (DataverseInfoValidationFormWithKey):\n%s" % api_prep_form.errors

        data_params = api_prep_form.get_api_params_with_signature()

        try:
            r = requests.post(DELETE_LAYER_API_PATH\
                               , data=data_params\
                            )
        except requests.exceptions.ConnectionError as e:
            msgx('Connection error: %s' % e.message)
        except:
            msgx("Unexpected error: %s" % sys.exc_info()[0])

        assert r.status_code == 200, "Expected status code 200 but received '%s'" % r.status_code
        msgn('Layer deleted: %s\n%s' % (r.status_code, r.text))


    def is_attribute_in_ma_layer(self, attr_name):
        if attr_name is None:
            return False

        print 'layer_attribute_info.__class__.__name__', self.layer_attribute_info.__class__.__name__
        print 'layer_attribute_info.__class__.__name__', self.layer_attribute_info
        for attr_dict in self.layer_attribute_info:
            print attr_dict, attr_dict.__class__
            if attr_dict.get('name', None) == attr_name:
                return True
        return False

    def test_01_upload_join_boston_income(self):

        msgt('(1) test_01_upload_join_boston_income')

        fname_to_upload = join(self.TEST_FILE_DIR, 'boston-income.csv')
        assert isfile(fname_to_upload), "File not found: %s" % fname_to_upload

        layer_attribute_name = 'TRACTCE'
        self.assertTrue(self.is_attribute_in_ma_layer(layer_attribute_name)\
                    , "Attribute '%s' not found in layer '%s'" % (layer_attribute_name, self.existing_layer_name))

        params = {
            'title' : 'Boston Income',
            'layer_typename' : self.existing_layer_name,  # Join Target
            'layer_attribute': layer_attribute_name, # underlying layer - attribute
            'table_attribute': 'tract', # data table - attribute
        }

        tr = TabularTest()
        tr.login_for_cookie()

        try:
            r = tr.upload_datatable_and_join_to_layer(params, fname_to_upload)
        except requests.exceptions.ConnectionError as e:
            msgx('Connection error: %s' % e.message)
        except:
            msgx("Unexpected error: %s" % sys.exc_info()[0])

        msg(r.status_code)
        msg(r.text)

        self.assertTrue(r.status_code==200\
                        , "Should receive 200 message.  Received: %s\n%s" % (r.status_code, r.text))

        try:
            rjson = r.json()
        except:
            self.assertTrue(False,  "Failed to convert response text to JSON. Text:\n%s" % r.text)


        msg(rjson)

        f = TableJoinResultForm(rjson)
        self.assertTrue(f.is_valid(), "Validation failed with TableJoinResultForm: %s" % f.errors)


        # api/(?P<dt_id>\d+)/remove

        #{u'tablejoin_id': 5, u'matched_record_count': 114, u'join_layer_typename': u'geonode:join_ma_tigerlines_zip_clq_boston_income', u'join_layer_id': u'91', u'unmatched_records_list': u'000501,000702,010101,010202,010401,050100,051100,060300,070100,070400,071200,080400,080800,000801,010102,010201,010402,020100,020300,050900,060100,060500,061100,071100,080600,081000,110200,120102,090900,091000,092100,100602,110100,110300,110402,110602,120101,120200,120300,130401,140103,140104', u'layer_typename': u'geonode:join_ma_tigerlines_zip_clq_boston_income', u'join_layer_url': u'/data/geonode:join_ma_tigerlines_zip_clq_boston_income', u'layer_join_attribute': u'TRACTCE', u'table_name': u'boston_income', u'tablejoin_view_name': u'join_ma_tigerlines_zip_clq_boston_income', u'unmatched_record_count': 42, u'table_join_attribute': u'tract'}


    @skip("skipping")
    def test_it2(self):
        msgt('------------ TEST IT 2------------')
        msg('Still got it? existing_layer_name: %s' % self.existing_layer_name)
        msg('Still got it? existing_layer_data: %s (truncated) ...' % str(self.existing_layer_data)[:100])


