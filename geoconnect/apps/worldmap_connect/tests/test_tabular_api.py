"""
Run tests for the WorldMap Shapefile import API

python manage.py test apps.worldmap_connect.tests.test_classify_layer.TestWorldMapClassification

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
from shared_dataverse_information.map_layer_metadata.forms import MapLayerMetadataValidationForm
from shared_dataverse_information.dataverse_info.forms_existing_layer import DataverseInfoValidationFormWithKey
from shared_dataverse_information.map_layer_metadata.forms import WorldMapToGeoconnectMapLayerMetadataValidationForm

from shared_dataverse_information.worldmap_api_helper.url_helper import CLASSIFY_LAYER_API_PATH\
                , GET_LAYER_INFO_BY_DATAVERSE_INSTALLATION_AND_FILE_API_PATH\
                , GET_CLASSIFY_ATTRIBUTES_API_PATH


# Validation forms from https://github.com/IQSS/shared-dataverse-information
#
#from shared_dataverse_information.worldmap_api_helper.forms_api_validate import SIGNATURE_KEY
#from shared_dataverse_information.map_layer_metadata.forms import WorldMapToGeoconnectMapLayerMetadataValidationForm
#from shared_dataverse_information.layer_classification.forms_api import ClassifyRequestDataForm, LayerAttributeRequestForm
#from shared_dataverse_information.dataverse_info.forms_existing_layer import CheckForExistingLayerForm

from geo_utils.msg_util import *

from worldmap_base_test import WorldMapBaseTest


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
        cls.existing_layer_name = rjson.get('data', {}).get('layer_name', None)
        cls.existing_layer_data = rjson.get('data', {})
        cls.layer_attribute_info = rjson.get('data', {}).get('attribute_info', None)

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


    def test_it(self):
        msgt('------------ TEST IT ------------')
        msg('existing_layer_name: %s' % self.existing_layer_name)
        msg('layer_attribute_info: %s' % self.layer_attribute_info)


    #@skip("skipping")
    def test_it2(self):
        msgt('------------ TEST IT 2------------')
        msg('Still got it? existing_layer_name: %s' % self.existing_layer_name)
        msg('Still got it? existing_layer_data: %s (truncated) ...' % str(self.existing_layer_data)[:100])


