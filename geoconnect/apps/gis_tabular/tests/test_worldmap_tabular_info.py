from os.path import abspath, dirname, isfile, join, isdir
import json
from unittest import skip

from django.test import TestCase
from django.core import management

from apps.gis_tabular.models import TabularFileInfo, WorldMapTabularLayerInfo
from apps.gis_tabular.tabular_helper import TabFileStats
from geo_utils.msg_util import msgt, msg


JSON_JOIN_TEST_FILENAME = join(dirname(__file__), 'input', 'core_data_join.json')

class WorldMapTabularLTestCase(TestCase):
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


    def test_01_initial_join(self):
        """Using WorldMap successful JSON response to test "build_from_worldmap_json"""
        msgt(self.test_01_initial_join.__doc__)

        tab_file_info = TabularFileInfo.objects.get(pk=15) # Election precinct test
        print tab_file_info.id
        self.assertEqual(tab_file_info.id, 15)

        # ------------------------------------------
        # Fail by passing a string instead of JSON
        # ------------------------------------------
        tab_map_info = WorldMapTabularLayerInfo.build_from_worldmap_json(tab_file_info, self.json_join_data_string)
        self.assertEqual(tab_map_info, None)

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


    def test_02_col_names_load(self):
        msgt(self.test_02_col_names_load.__doc__)

        # grab a tabular file obj
        tab_file_info = TabularFileInfo.objects.get(pk=14) # Election precinct test

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
