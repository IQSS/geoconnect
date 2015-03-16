"""
Run tests for the WorldMap Shapefile import API

python manage.py test apps.worldmap_connect.tests.test_classify_layer.TestWorldMapClassification

"""

import requests
from os.path import abspath, dirname, isfile, join, isdir

import json

# API path(s) are here
#
from shared_dataverse_information.worldmap_api_helper.url_helper import CLASSIFY_LAYER_API_PATH\
                , GET_LAYER_INFO_BY_DATAVERSE_INSTALLATION_AND_FILE_API_PATH\
                , GET_CLASSIFY_ATTRIBUTES_API_PATH


# Validation forms from https://github.com/IQSS/shared-dataverse-information
#
from shared_dataverse_information.worldmap_api_helper.forms_api_validate import SIGNATURE_KEY
from shared_dataverse_information.map_layer_metadata.forms import WorldMapToGeoconnectMapLayerMetadataValidationForm
from shared_dataverse_information.layer_classification.forms_api import ClassifyRequestDataForm, LayerAttributeRequestForm
from shared_dataverse_information.dataverse_info.forms_existing_layer import CheckForExistingLayerForm

from geo_utils.msg_util import *

from test_shapefile_import import TestWorldMapShapefileImport
from worldmap_base_test import WorldMapBaseTest


class TestWorldMapClassification(WorldMapBaseTest):

    def setUp(self):
        super(TestWorldMapClassification, self).setUp()              #super().__init__(x,y)
        #msgt('........ set up 2 ................')
        
        self.existing_layer_name = None
        
        # Add a shapefile - also a test
        shp_import = TestWorldMapShapefileImport('test02_good_shapefile_import')
        shp_import.setUp()
        shp_import.test02_good_shapefile_import()
        
    def tearDown(self):
        super(TestWorldMapClassification, self).tearDown()              #super().__init__(x,y)

        # Remove the shapefile - also a test
        shp_import = TestWorldMapShapefileImport('test04_good_delete_shapefile_from_worldmap')
        shp_import.setUp()
        shp_import.test04_good_delete_shapefile_from_worldmap()



    def test01_good_classification(self):

        # Note: This has to be imported AFTER WorldMapBaseTest setUp creates a test table
        #
        
        #-----------------------------------------------------------
        msgt("--- Classification calls that should fail ---")
        #-----------------------------------------------------------

        #-----------------------------------------------------------
        msgn("(1a) Retrieve layer information based on datafile_id and dv_user_id")
        #-----------------------------------------------------------
        api_layer_info_url = GET_LAYER_INFO_BY_DATAVERSE_INSTALLATION_AND_FILE_API_PATH
        msg('api_layer_info_url: %s' % api_layer_info_url)
        
        f = CheckForExistingLayerForm(self.dataverse_test_info)
        self.assertTrue(f.is_valid(), 'Validation failed using CheckForExistingLayerForm')
        
        # Retrieve Layer metata using datafile_id and dv_user_id
        # e.g.  {'datafile_id': 1388, 'dv_user_id': 1}
        params = f.get_api_params_with_signature()
        
        msgn('PARAMS: %s' %params)
        try:
            r = requests.post(api_layer_info_url, data=params)
        except requests.exceptions.ConnectionError as e:
            msgx('Connection error: %s' % e.message)
        except:
            msgx("Unexpected error: %s" % sys.exc_info()[0])

        self.assertEquals(r.status_code, 200, "Expected status code of 200 but received '%s'" % r.status_code)
        

        #-----------------------------------------------------------
        msgn("(1b) Convert response to JSON")
        #-----------------------------------------------------------
        try:
            rjson = r.json()
        except:
            self.assertTrue(False, "Failed to convert response text to JSON. Text:\n%s" % r.text)
        
        #-----------------------------------------------------------
        msgn("(1c) Check for key fields in JSON")
        #-----------------------------------------------------------
        msg(rjson)
        self.assertTrue(rjson.has_key('success'), "JSON did not have key 'success'. Keys found:\n %s" % rjson.keys())
        self.assertTrue(rjson.has_key('data'), "JSON did not have key 'data'. Keys found:\n %s" % rjson.keys())

        self.assertEquals(rjson.get('success'), True, "Expected 'success' value to be 'True'.  Found: '%s'" % rjson.get('success'))
        
        
        #-----------------------------------------------------------
        msgn("(1d) Validate returned data using WorldMapToGeoconnectMapLayerMetadataValidationForm\n(includes layer name)")
        #-----------------------------------------------------------
        f = WorldMapToGeoconnectMapLayerMetadataValidationForm(rjson.get('data', {}))
        
        self.assertTrue(f.is_valid(), 'Validation failed using WorldMapToGeoconnectMapLayerMetadataValidationForm. Errors: %s' % f.errors)


        #-----------------------------------------------------------
        msgn("(1e) Get layer name from data (confirmed by previous validation)")
        #-----------------------------------------------------------
        self.existing_layer_name  = rjson.get('data', {}).get('layer_name', None)
        self.assertTrue( self.existing_layer_name is not None, 'self.existing_layer_name cannot be None')
        self.assertTrue( len(self.existing_layer_name) > 0, 'self.existing_layer_name cannot be length 0')
        
        #-----------------------------------------------------------
        msgn("(1f) Prepare classification call")
        #-----------------------------------------------------------
        api_classify_layer_url = CLASSIFY_LAYER_API_PATH
        msg('api_classify_layer_url: %s' % api_classify_layer_url)
        msg('existing_layer_name: %s' % self.existing_layer_name)
        #self.dataverse_test_info 
        
        
        initial_classify_params = {'reverse': False\
                        		, 'attribute': 'SocStrife1'\
                        		, 'ramp': 'Custom'\
                        		, 'endColor': '#f16913'\
                        		, 'intervals': 5\
                        		, 'layer_name': self.existing_layer_name\
                        		, 'startColor': '#fff5eb'\
                        		, 'method': 'jenks'\
                        		}
        
        initial_classify_params.update(self.dataverse_test_info)
        
        f_classify = ClassifyRequestDataForm(initial_classify_params)
        self.assertTrue(f_classify.is_valid(), 'ClassifyRequestDataForm did not validate. Errors:\n %s' % f_classify.errors)
        
        classify_params = f_classify.get_api_params_with_signature()
        msgt('classify_params: %s' % classify_params)
        self.assertTrue(classify_params.has_key(SIGNATURE_KEY)\
                        , 'classify_params did not have SIGNATURE_KEY: "%s"' % SIGNATURE_KEY)

                        
        #-----------------------------------------------------------
        msgn("(1g) Make classification request")
        #-----------------------------------------------------------
        try:
            r = requests.post(api_classify_layer_url, data=classify_params)
        except requests.exceptions.ConnectionError as e:
            msgx('Connection error: %s' % e.message)
        except:
            msgx("Unexpected error: %s" % sys.exc_info()[0])

        print r.text
        print r.status_code

        self.assertEquals(r.status_code, 200, "Expected status code of 200 but received '%s'" % r.status_code)
        
        #-----------------------------------------------------------
        msgn("(1h) Convert response to JSON")
        #-----------------------------------------------------------
        try:
            json_resp = r.json()
        except:
            self.assertTrue(False, "Failed to convert response text to JSON. Text:\n%s" % r.text)

        print 'json_resp: %s' % json_resp

        self.assertTrue(json_resp.has_key('success'), 'JSON should have key "success".  But found keys: %s' % json_resp.keys())
        self.assertEqual(json_resp.get('success'), True, "'success' value should be 'True'")

        f_metadata_check = WorldMapToGeoconnectMapLayerMetadataValidationForm(json_resp.get('data', None))
        self.assertTrue(f_metadata_check.is_valid(), "Validation failed for WorldMapToGeoconnectMapLayerMetadataValidationForm. Errors: %s" % f_metadata_check.errors)
        
        
        #-----------------------------------------------------------
        msgn("(1i) Retrieve classification params")
        #-----------------------------------------------------------        
        params_for_attr_request = self.dataverse_test_info
        params_for_attr_request['layer_name'] = self.existing_layer_name
        f_attrs = LayerAttributeRequestForm(params_for_attr_request)
        self.assertTrue(f_attrs.is_valid(), 'ClassifyRequestDataForm did not validate. Errors:\n %s' % f_attrs.errors)
        
        retrieve_attribute_params = f_attrs.get_api_params_with_signature()
        msgt('retrieve_attribute_params: %s' % retrieve_attribute_params)
        self.assertTrue(retrieve_attribute_params.has_key(SIGNATURE_KEY)\
                        , 'classify_params did not have SIGNATURE_KEY: "%s"' % SIGNATURE_KEY)
        
        #-----------------------------------------------------------
        msgn("(1i) Make classification param request")
        #-----------------------------------------------------------
        try:
            r = requests.post(GET_CLASSIFY_ATTRIBUTES_API_PATH, data=retrieve_attribute_params)
        except requests.exceptions.ConnectionError as e:
            msgx('Connection error: %s' % e.message)
        except:
            msgx("Unexpected error: %s" % sys.exc_info()[0])

        print r.status_code
        self.assertEquals(r.status_code, 200, "Expected status code of 200 but received '%s'" % r.status_code)

        try:
            json_resp = r.json()
        except:
            self.assertTrue(False, "Failed to convert response text to JSON. Text:\n%s" % r.text)

        self.assertTrue(json_resp.has_key('success'), 'JSON should have key "success".  But found keys: %s' % json_resp.keys())
        self.assertEqual(json_resp.get('success'), True, "'success' value should be 'True'")

        self.assertTrue(json_resp.has_key('data'), 'JSON should have key "success".  But found keys: %s' % json_resp.keys())
        
        attribute_data = json_resp.get('data', None)
        self.assertTrue(attribute_data is not None, "attribute_data was None")
        
        print attribute_data
        self.assertEqual(len(attribute_data), 54, "Should be 54 attributes but found only %s" % len(attribute_data))
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
