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


from geo_utils.msg_util import *


# --------------------------------------------------
# Load up the Worldmap server url and username
# --------------------------------------------------
GEONODE_CREDS_FNAME = join(dirname(realpath(__file__)), 'server_creds.json')
assert isfile(GEONODE_CREDS_FNAME), 'Server credentials file not found: %s' % GEONODE_CREDS_FNAME
try:
    GEONODE_CREDS_JSON = json.loads(open(GEONODE_CREDS_FNAME, 'r').read())
except:
    raise Exception('Could not parse tabular credentials JSON file: %s' % 'server_creds.json')

GEONODE_SERVER = GEONODE_CREDS_JSON['SERVER_URL']
GEONODE_USERNAME = GEONODE_CREDS_JSON['USERNAME']
GEONODE_PASSWORD = GEONODE_CREDS_JSON['PASSWORD']

#INPUT_DIR = join('..', 'input')


def setUpModule():
    msg( '---- Module setup ---- ')

def tearDownModule():
    msg( '---- Module teardown ---- ')


class TestWorldMapTabularAPI(TestCase):


    TEST_FILE_DIR = join(dirname(realpath(__file__)), 'input')
    existing_layer_name = None
    existing_layer_data = None
    layer_attribute_info = None
    
    URL_ID_ATTR = 'URL_ID'
    
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
    def setUp(self):
        global GEONODE_SERVER, GEONODE_USERNAME, GEONODE_PASSWORD
        self.client = requests.session()
        self.base_url = GEONODE_SERVER

        self.geonode_username = GEONODE_USERNAME
        self.geonode_password = GEONODE_PASSWORD

        #self.login_url =  self.base_url + "/account/login/" # GeoNode
        self.login_url =  self.base_url + "/accounts/login/" # WorldMap
        self.csv_upload_url  = self.base_url + '/datatables/api/upload'
        #self.shp_layer_upload_url = self.base_url + '/layers/upload'
        self.join_datatable_url = self.base_url + '/datatables/api/join'
        self.upload_and_join_datatable_url = self.base_url + '/datatables/api/upload_and_join'
        self.upload_lat_lng_url = self.base_url + '/datatables/api/upload_lat_lon'

        self.datatable_detail = self.base_url + '/datatables/api/%s' % self.URL_ID_ATTR
        self.delete_datatable_url = self.base_url + '/datatables/api/%s/remove' % self.URL_ID_ATTR

        self.tablejoin_detail = self.base_url + '/datatables/api/join/%s' % self.URL_ID_ATTR
        self.delete_tablejoin_url = self.base_url + '/datatables/api/join/%s/remove' % self.URL_ID_ATTR


    def login_for_cookie(self):

        msg('login_for_cookie: %s' % self.login_url)

        # Retrieve the CSRF token first
        self.client.get(self.login_url)  # sets the cookie
        csrftoken = self.client.cookies['csrftoken']

        login_data = dict(username=self.geonode_username\
                        , password=self.geonode_password\
                        , csrfmiddlewaretoken=csrftoken\
                        )
        #headers=dict(Referer=URL)
        r = self.client.post(self.login_url\
                            , data=login_data\
                            , headers={"Referer": self.login_url}\
                            #, headers={"Referer": "test-client"}\
                            )

        #print r.text
        self.assertTrue(r.status_code==200\
            , "Login for cookie failed.  Rcvd status code: %s\nText: %s" % (r.status_code, r.text))


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


    @skip('skipping test_01_datatable_fail_tests')
    def test_01_datatable_fail_tests(self):

        msgt('(1) test_01_datatable_fail_tests')

        # --------------------------------
        # Initial test params
        # --------------------------------
        layer_attribute_name = 'TRACTCE'
        fname_to_upload = join(self.TEST_FILE_DIR, 'boston-income.csv')
        assert isfile(fname_to_upload), "File not found: %s" % fname_to_upload

        params = {
            'title' : 'Boston Income',
            'layer_typename' : self.existing_layer_name,  # Join Target
            'layer_attribute': layer_attribute_name, # underlying layer - attribute
            'table_attribute': 'tract', # data table - attribute
        }

        #-----------------------------------------------------------
        msgn('(1a) Fail with no file')
        #-----------------------------------------------------------
        self.login_for_cookie()

        try:
            r = self.client.post(self.upload_and_join_datatable_url\
                                        , data=params\
            #                            , files=files\
                                    )
        except requests.exceptions.ConnectionError as e:
            msgx('Connection error: %s' % e.message)
        except:
            msgx("Unexpected error: %s" % sys.exc_info()[0])


        self.assertTrue(r.status_code==400, "Status code should be 400.  Found: %s" % r.status_code)

        try:
            rjson = r.json()
        except:
            self.assertTrue(False,  "Failed to convert response text to JSON. Text:\n%s" % r.text)
            return

        self.assertTrue(rjson.has_key('success')\
                        , "JSON 'success' attribute not found in JSON result: %s" % rjson)

        self.assertTrue(rjson.get('success', None) is False\
                        , "JSON 'success' attribute should be 'false'. Found: %s" % rjson)

        self.assertTrue(rjson.has_key('data')\
                        , "JSON 'data' attribute not found in JSON result: %s" % rjson)

        self.assertTrue(rjson.get('data', {}).has_key('uploaded_file')\
                        , "JSON 'data' attribute have an 'uploaded_file' key. Found: %s" % rjson)

        self.assertTrue(r.text.find('This field is required.') > -1\
                        , "Response text should have error of 'This field is required.'  Found: %s" % rjson)

        #-----------------------------------------------------------
        msgn('(1b) Fail with blank title')
        #-----------------------------------------------------------


        params2 = params.copy()
        params2['title'] = ''

        self.login_for_cookie()

        files = {'uploaded_file': open(fname_to_upload,'rb')}
        try:
            r = self.client.post(self.upload_and_join_datatable_url\
                                        , data=params\
                                        , files=files\
                                    )
        except requests.exceptions.ConnectionError as e:
            msgx('Connection error: %s' % e.message)
        except:
            msgx("Unexpected error: %s" % sys.exc_info()[0])


        msg(r.text)
        msg(r.status_code)

        self.assertTrue(r.status_code==400, "Status code should be 400.  Found: %s" % r.status_code)
        return
        try:
            rjson = r.json()
        except:
            self.assertTrue(False,  "Failed to convert response text to JSON. Text:\n%s" % r.text)
            return

        msg(r.text)
        msg(r.status_code)
        self.assertTrue(rjson.has_key('success')\
                        , "JSON 'success' attribute not found in JSON result: %s" % rjson)

        self.assertTrue(rjson.get('success', None) is False\
                        , "JSON 'success' attribute should be 'false'. Found: %s" % rjson)

        self.assertTrue(rjson.has_key('data')\
                        , "JSON 'data' attribute not found in JSON result: %s" % rjson)

        #self.assertTrue(rjson.get('data', {}).has_key('uploaded_file')\
        #                , "JSON 'data' attribute have an 'uploaded_file' key. Found: %s" % rjson)

        #self.assertTrue(r.text.find('This field is required.') > -1\
        #                , "Response text should have error of 'This field is required.'  Found: %s" % rjson)
        #msg(r.text)
        #msg(r.status_code)

    def test_04_non_existent_tablejoin(self):

        #-----------------------------------------------------------
        msgn("(4) TableJoin - try to see details and delete with bad id")
        #-----------------------------------------------------------
        table_join_id = 8723552 # test will fail is this id exists

        #-----------------------------------------------------------
        msgn("(4a) Try to view with bad id")
        #-----------------------------------------------------------
        api_tj_detail_url = self.tablejoin_detail.replace(self.URL_ID_ATTR, str(table_join_id))
        msg('api_tj_detail_url: %s' % api_tj_detail_url)

        self.login_for_cookie()

        try:
            r = self.client.get(api_tj_detail_url)
        except requests.exceptions.ConnectionError as e:
            msgx('Connection error: %s' % e.message)
        except:
            msgx("Unexpected error: %s" % sys.exc_info()[0])

        msg(r.text)
        msg('status_code: %s' % r.status_code)


        if r.status_code==404:
            msg('(success) TableJoin id not found')
        else:
            self.assertTrue(False\
                   , "Should receive 404 message.  Received: %s\n%s" % (r.status_code, r.text))


        #-----------------------------------------------------------
        msgn("(4b) Try to delete with bad id")
        #-----------------------------------------------------------
        api_del_tablejoin_url = self.delete_tablejoin_url.replace(self.URL_ID_ATTR, str(table_join_id))
        msg('api_del_tablejoin_url: %s' % api_del_tablejoin_url)

        self.login_for_cookie()

        try:
            r = self.client.get(api_del_tablejoin_url)
        except requests.exceptions.ConnectionError as e:
            msgx('Connection error: %s' % e.message)
        except:
            msgx("Unexpected error: %s" % sys.exc_info()[0])

        msg(r.text)
        msg('status_code: %s' % r.status_code)


        if r.status_code==404:
            msg('(success) TableJoin id not found')
        else:
            self.assertTrue(False\
                   , "Should receive 404 message.  Received: %s\n%s" % (r.status_code, r.text))


    @skip('skipping test_02_upload_join_boston_income')
    def test_02_upload_join_boston_income(self):

        msgt('(2) Good Upload and Join - Delete TableJoin (test_02_upload_join_boston_income)')

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


        #-----------------------------------------------------------
        msgn('(2a) Upload table and join layer')
        #-----------------------------------------------------------
        self.login_for_cookie()

        files = {'uploaded_file': open(fname_to_upload,'rb')}
        try:
            r = self.client.post(self.upload_and_join_datatable_url\
                                        , data=params\
                                        , files=files\
                                    )
        except requests.exceptions.ConnectionError as e:
            msgx('Connection error: %s' % e.message)
        except:
            msgx("Unexpected error: %s" % sys.exc_info()[0])

        msg(r.status_code)
        #msg(r.text)

        if r.status_code == 200:
            msg('DataTable uploaded and joined!')
        else:
            self.assertTrue(False\
                        , "Should receive 200 message.  Received: %s\n%s" % (r.status_code, r.text))

        try:
            rjson = r.json()
        except:
            self.assertTrue(False,  "Failed to convert response text to JSON. Text:\n%s" % r.text)

        msg(rjson)

        f = TableJoinResultForm(rjson)
        self.assertTrue(f.is_valid(), "Validation failed with TableJoinResultForm: %s" % f.errors)

        #-----------------------------------------------------------
        # Pull out table_id and tablejoin_id
        #   for detail and delete tests
        #-----------------------------------------------------------
        table_id = f.cleaned_data.get('table_id', None)
        self.assertTrue(table_id is not None\
                , "table_id should not be None. cleaned form data: %s" % f.cleaned_data)

        tablejoin_id = f.cleaned_data.get('tablejoin_id', None)
        self.assertTrue(tablejoin_id is not None\
                , "tablejoin_id should not be None. cleaned form data: %s" % f.cleaned_data)


        #-----------------------------------------------------------
        msgn('(2b) DataTable Detail')
        #-----------------------------------------------------------
        api_detail_url = self.datatable_detail.replace(self.URL_ID_ATTR, str(table_id))

        self.login_for_cookie()

        r = None
        try:
            r = self.client.get(api_detail_url)
        except requests.exceptions.ConnectionError as e:
            msgx('Connection error: %s' % e.message)
        except:
            msgx("Unexpected error: %s" % sys.exc_info()[0])

        self.assertTrue(r.status_code==200\
                        , "Should receive 200 message.  Received: %s\n%s" % (r.status_code, r.text))

        if r.status_code==200:
            msg('DataTable detail: %s' % r.text)
        else:
            self.assertTrue(False\
                   , "Should receive 200 message.  Received: %s\n%s" % (r.status_code, r.text))


        #-----------------------------------------------------------
        msgn('(2c) TableJoin Detail')
        #-----------------------------------------------------------
        api_detail_url = self.tablejoin_detail.replace(self.URL_ID_ATTR, str(tablejoin_id))

        self.login_for_cookie()

        r = None
        try:
            r = self.client.get(api_detail_url)
        except requests.exceptions.ConnectionError as e:
            msgx('Connection error: %s' % e.message)
        except:
            msgx("Unexpected error: %s" % sys.exc_info()[0])

        self.assertTrue(r.status_code==200\
                        , "Should receive 200 message.  Received: %s\n%s" % (r.status_code, r.text))

        if r.status_code==200:
            msg('TableJoin detail: %s' % r.text)
        else:
            self.assertTrue(False\
                   , "Should receive 200 message.  Received: %s\n%s" % (r.status_code, r.text))

        #-----------------------------------------------------------
        msgn('(2e) TableJoin Delete -- also deletes TableJoin')
        #-----------------------------------------------------------

        api_del_tablejoin_url = self.delete_tablejoin_url.replace(self.URL_ID_ATTR, str(tablejoin_id))
        msg('api_del_tablejoin_url: %s' % api_del_tablejoin_url)

        self.login_for_cookie()

        try:
            r = self.client.get(api_del_tablejoin_url)
        except requests.exceptions.ConnectionError as e:
            msgx('Connection error: %s' % e.message)
        except:
            msgx("Unexpected error: %s" % sys.exc_info()[0])

        msg(r.text)
        msg('status_code: %s' % r.status_code)

        self.assertTrue(r.status_code==200\
                        , "Should receive 200 message.  Received: %s\n%s" % (r.status_code, r.text))

        if r.status_code==200:
            msg('TableJoin deleted: %s' % r.text)
        else:
            self.assertTrue(False\
                   , "Should receive 200 message.  Received: %s\n%s" % (r.status_code, r.text))

      



    @skip('skipping test_03_upload_join_boston_income')
    def test_03_upload_join_boston_income(self):

        msgt('(3) Good Upload and Join - Delete DataTable (test_03_upload_join_boston_income)')

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


        #-----------------------------------------------------------
        msgn('(3a) Upload table and join layer')
        #-----------------------------------------------------------
        self.login_for_cookie()

        files = {'uploaded_file': open(fname_to_upload,'rb')}
        try:
            r = self.client.post(self.upload_and_join_datatable_url\
                                        , data=params\
                                        , files=files\
                                    )
        except requests.exceptions.ConnectionError as e:
            msgx('Connection error: %s' % e.message)
        except:
            msgx("Unexpected error: %s" % sys.exc_info()[0])

        msg(r.status_code)
        #msg(r.text)

        if r.status_code == 200:
            msg('DataTable uploaded and joined!')
        else:
            self.assertTrue(False\
                        , "Should receive 200 message.  Received: %s\n%s" % (r.status_code, r.text))

        try:
            rjson = r.json()
        except:
            self.assertTrue(False,  "Failed to convert response text to JSON. Text:\n%s" % r.text)

        msg(rjson)

        f = TableJoinResultForm(rjson)
        self.assertTrue(f.is_valid(), "Validation failed with TableJoinResultForm: %s" % f.errors)

        #-----------------------------------------------------------
        # Pull out table_id and tablejoin_id
        #   for detail and delete tests
        #-----------------------------------------------------------
        table_id = f.cleaned_data.get('table_id', None)
        self.assertTrue(table_id is not None\
                , "table_id should not be None. cleaned form data: %s" % f.cleaned_data)

        tablejoin_id = f.cleaned_data.get('tablejoin_id', None)
        self.assertTrue(tablejoin_id is not None\
                , "tablejoin_id should not be None. cleaned form data: %s" % f.cleaned_data)


        #-----------------------------------------------------------
        msgn('(3b) DataTable Detail')
        #-----------------------------------------------------------
        api_detail_url = self.datatable_detail.replace(self.URL_ID_ATTR, str(table_id))

        self.login_for_cookie()

        r = None
        try:
            r = self.client.get(api_detail_url)
        except requests.exceptions.ConnectionError as e:
            msgx('Connection error: %s' % e.message)
        except:
            msgx("Unexpected error: %s" % sys.exc_info()[0])

        self.assertTrue(r.status_code==200\
                        , "Should receive 200 message.  Received: %s\n%s" % (r.status_code, r.text))

        if r.status_code==200:
            msg('DataTable detail: %s' % r.text)
        else:
            self.assertTrue(False\
                   , "Should receive 200 message.  Received: %s\n%s" % (r.status_code, r.text))


        #-----------------------------------------------------------
        msgn('(3c) TableJoin Detail')
        #-----------------------------------------------------------
        api_detail_url = self.tablejoin_detail.replace(self.URL_ID_ATTR, str(tablejoin_id))

        self.login_for_cookie()

        r = None
        try:
            r = self.client.get(api_detail_url)
        except requests.exceptions.ConnectionError as e:
            msgx('Connection error: %s' % e.message)
        except:
            msgx("Unexpected error: %s" % sys.exc_info()[0])

        self.assertTrue(r.status_code==200\
                        , "Should receive 200 message.  Received: %s\n%s" % (r.status_code, r.text))

        if r.status_code==200:
            msg('TableJoin detail: %s' % r.text)
        else:
            self.assertTrue(False\
                   , "Should receive 200 message.  Received: %s\n%s" % (r.status_code, r.text))


        #-----------------------------------------------------------
        msgn('(3d) Delete DataTable')
        #-----------------------------------------------------------
        api_del_url = self.delete_datatable_url.replace(self.URL_ID_ATTR, str(table_id))
        msg('api_del_url: %s' % api_del_url)

        self.login_for_cookie()
        r = None
        try:
            r = self.client.get(api_del_url)
        except requests.exceptions.ConnectionError as e:
            msgx('Connection error: %s' % e.message)
        except:
            msgx("Unexpected error: %s" % sys.exc_info()[0])

        #msg(r.status_code)
        #msg(r.text)

        self.assertTrue(r.status_code==200\
                        , "Should receive 200 message.  Received: %s\n%s" % (r.status_code, r.text))

        if r.status_code==200:
            msg('DataTable deleted: %s' % r.text)
        else:
            self.assertTrue(False\
                   , "Should receive 200 message.  Received: %s\n%s" % (r.status_code, r.text))


    @skip("skipping")
    def test_it2(self):
        msgt('------------ TEST IT 2------------')
        msg('Still got it? existing_layer_name: %s' % self.existing_layer_name)
        msg('Still got it? existing_layer_data: %s (truncated) ...' % str(self.existing_layer_data)[:100])

