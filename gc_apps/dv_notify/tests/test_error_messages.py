from __future__ import print_function
from os.path import abspath, dirname, isfile, join, isdir
import json
from unittest import skip

from django.test import TestCase
from django.core import management
from django.core.files import File

from gc_apps.gis_tabular.models import TabularFileInfo, WorldMapTabularLayerInfo
from gc_apps.gis_tabular.tabular_helper import TabFileStats
from gc_apps.geo_utils.msg_util import msgt, msg
from gc_apps.dv_notify.metadata_updater import MetadataUpdater,\
        ERROR_DV_PAGE_NOT_FOUND,\
        ERROR_DV_NO_SERVER_RESPONSE,\
        ERROR_DV_METADATA_UPDATE

JSON_JOIN_TEST_FILENAME = join(dirname(__file__), 'input', 'core_data_join.json')


class TestDataverseNotify(TestCase):
    """
    Test basic params
    """

    def setUp(self):
        print ('load JSON file + fixtures')
        self.json_join_data_string = open(JSON_JOIN_TEST_FILENAME, 'r').read()
        #self.join_targets_json = json.loads(json_data)

        management.call_command('loaddata', 'test_join_layer-2016-1205.json')#, verbosity=)

    def tearDown(self):
        print ('flush fixtures')
        management.call_command('flush', verbosity=3, interactive=False)


    @skip('test_01_update_dataverse_metadata')
    def test_01_update_dataverse_metadata(self):
        """Test Dataverse "update metadata" url endpoint. Only testing
        fail conditions, e.g. can't contact server, etc."""
        msgt(self.test_01_update_dataverse_metadata.__doc__)

        tab_file_info = TabularFileInfo.objects.get(pk=15) # Election precinct test

        # --------------------------------------------
        #  Attach actual file -- path from fixture is not correct
        # --------------------------------------------
        elect_filepath = join(dirname(__file__),
                            'input',
                            'election_precincts2.csv')
        tab_file_info.dv_file.save(\
                        'election_precincts2.csv',
                        File(open(elect_filepath, 'r')),
                        save=False)


        self.assertEqual(tab_file_info.id, 15)

        # ------------------------------------------
        # Load successful info
        # ------------------------------------------
        tab_map_info = WorldMapTabularLayerInfo.build_from_worldmap_json(\
                            tab_file_info,\
                            json.loads(self.json_join_data_string))
        self.assertTrue(tab_map_info.id is not None)

        # ------------------------------------------
        # Make sure data loading as expected
        # ------------------------------------------
        self.assertEqual(type(tab_map_info.core_data), dict)
        self.assertEqual(type(tab_map_info.attribute_data), list)
        self.assertEqual(type(tab_map_info.download_links), dict)


        # ------------------------------------------
        # Send message to non-existent server
        # ------------------------------------------
        msgt('Send message to non-existent server')
        url_non_existent = 'https://nope.dataverse.harvard.edu'

        success, resp_dict = MetadataUpdater.update_dataverse_with_metadata(\
                                    tab_map_info,
                                    url_non_existent)

        self.assertEqual(success, False)
        self.assertTrue(resp_dict['message'].startswith(\
                        ERROR_DV_NO_SERVER_RESPONSE))

        # ------------------------------------------
        # Send message to server without an endpoint
        # ------------------------------------------
        msgt('Send message to server without an endpoint')
        url_no_endpoint = 'http://www.harvard.edu'

        success, resp_dict = MetadataUpdater.update_dataverse_with_metadata(\
                                    tab_map_info,
                                    url_no_endpoint)

        self.assertEqual(success, False)
        self.assertTrue(resp_dict['message'].startswith(\
                        ERROR_DV_PAGE_NOT_FOUND))

        # ------------------------------------------
        # No token in request to Dataverse
        # ------------------------------------------
        msgt(('No token in request to Dataverse'
             ' (requires working endpoint at https://dataverse.harvard.edu)'))
        url_no_endpoint = 'https://dataverse.harvard.edu'

        success, resp_dict = MetadataUpdater.update_dataverse_with_metadata(\
                                    tab_map_info,
                                    url_no_endpoint)

        self.assertEqual(success, False)
        self.assertEqual(resp_dict['message'], 'Token not found in JSON request.')


    def test_02_delete_dataverse_metadata(self):
        """Test Dataverse "delete metadata" url endpoint. Only testing
        fail conditions, e.g. can't contact server, etc."""
        msgt(self.test_02_delete_dataverse_metadata.__doc__)

        tab_file_info = TabularFileInfo.objects.get(pk=15) # Election precinct test

        # --------------------------------------------
        #  Attach actual file -- path from fixture is not correct
        # --------------------------------------------
        elect_filepath = join(dirname(__file__),
                            'input',
                            'election_precincts2.csv')
        tab_file_info.dv_file.save(\
                        'election_precincts2.csv',
                        File(open(elect_filepath, 'r')),
                        save=False)


        self.assertEqual(tab_file_info.id, 15)

        # ------------------------------------------
        # Load successful info
        # ------------------------------------------
        tab_map_info = WorldMapTabularLayerInfo.build_from_worldmap_json(\
                            tab_file_info,\
                            json.loads(self.json_join_data_string))
        self.assertTrue(tab_map_info.id is not None)

        # ------------------------------------------
        # Make sure data loading as expected
        # ------------------------------------------
        self.assertEqual(type(tab_map_info.core_data), dict)
        self.assertEqual(type(tab_map_info.attribute_data), list)
        self.assertEqual(type(tab_map_info.download_links), dict)


        # ------------------------------------------
        # Send message to non-existent server
        # ------------------------------------------
        msgt('Send message to non-existent server')
        url_non_existent = 'https://nope.dataverse.harvard.edu'

        success, err_msg_or_None = MetadataUpdater.delete_dataverse_map_metadata(\
                                    tab_map_info,
                                    url_non_existent)

        self.assertEqual(success, False)
        self.assertTrue(err_msg_or_None.startswith(\
                        ERROR_DV_NO_SERVER_RESPONSE))

        # ------------------------------------------
        # Send message to server without an endpoint
        # ------------------------------------------
        msgt('Send message to server without an endpoint')
        url_no_endpoint = 'http://www.harvard.edu'

        success, err_msg_or_None = MetadataUpdater.delete_dataverse_map_metadata(\
                                    tab_map_info,
                                    url_no_endpoint)

        self.assertEqual(success, False)
        self.assertTrue(err_msg_or_None.startswith(\
                        ERROR_DV_PAGE_NOT_FOUND))

        # ------------------------------------------
        # No token in request to Dataverse
        # ------------------------------------------
        msgt(('No token in request to Dataverse'
             ' (requires working endpoint at https://dataverse.harvard.edu)'))
        url_no_endpoint = 'https://dataverse.harvard.edu'

        success, err_msg_or_None = MetadataUpdater.delete_dataverse_map_metadata(\
                                    tab_map_info,
                                    url_no_endpoint)

        self.assertEqual(success, False)
        self.assertEqual(err_msg_or_None, 'Token not found in JSON request.')
