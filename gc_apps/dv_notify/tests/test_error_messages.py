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


    def test_01_update_dataverse_metadata(self):
        """Test Dataverse update url endpoint. Only testing
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


    @skip('skipping test_02_col_names_load')
    def test_02_col_names_load(self):
        msgt(self.test_02_col_names_load.__doc__)

        # grab a tabular file obj
        tab_file_info = TabularFileInfo.objects.get(pk=14) # Election precinct test

        # --------------------------------------------
        #  Attach actual file -- path from fixture is not correct
        # --------------------------------------------
        cbg_filepath = join(dirname(__file__),
                            'input',
                            'CBG_Annual_and_Longitudinal_Measures.tab')
        tab_file_info.dv_file.save(\
                        'CBG_Annual_and_Longitudinal_Measures',
                        File(open(cbg_filepath, 'r')),
                        save=False)

        # clear out the column info
        tab_file_info.column_names = None
        tab_file_info.save()

        # re-run column info
        tab_file_stats = TabFileStats.create_tab_stats_from_tabular_info(tab_file_info)
        self.assertTrue(not tab_file_stats.has_error())

        # Make sure num_rows and num_columns are the same
        self.assertEqual(tab_file_stats.tabular_info.num_rows, 554)
        self.assertEqual(tab_file_stats.tabular_info.num_columns, 49)

        # Is column_names a python list?
        self.assertEqual(type(tab_file_info.column_names), list)

        # Are the column_names correct?
        expected_colnames = ['BG_ID_10', 'DisSens_2010', 'PublicDenigration_2010', 'PrivateNeglect_2010', 'Housing_2010', 'UncivilUse_2010', 'BigBuild_2010', 'Trash_2010', 'Graffiti_2010', 'DisSens_2011', 'PublicDenigration_2011', 'PrivateNeglect_2011', 'Housing_2011', 'UncivilUse_2011', 'BigBuild_2011', 'Trash_2011', 'Graffiti_2011', 'DisSens_2012', 'PublicDenigration_2012', 'PrivateNeglect_2012', 'Housing_2012', 'UncivilUse_2012', 'BigBuild_2012', 'Trash_2012', 'Graffiti_2012', 'DisSens_2013', 'PublicDenigration_2013', 'PrivateNeglect_2013', 'Housing_2013', 'UncivilUse_2013', 'BigBuild_2013', 'Trash_2013', 'Graffiti_2013', 'DisSens_2014', 'PublicDenigration_2014', 'PrivateNeglect_2014', 'Housing_2014', 'UncivilUse_2014', 'BigBuild_2014', 'Trash_2014', 'Graffiti_2014', 'DisSens_long', 'PublicDenigration_long', 'PrivateNeglect_long', 'Housing_long', 'UncivilUse_long', 'BigBuild_long', 'Trash_long', 'Graffiti_long']
        self.assertEqual(tab_file_info.column_names, expected_colnames)
