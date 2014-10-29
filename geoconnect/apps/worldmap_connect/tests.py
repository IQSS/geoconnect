import unittest
from django.test import TestCase
from apps.worldmap_connect.worldmap_importer import WorldMapImporter
from StringIO import StringIO
from os.path import abspath, dirname, isfile, realpath, join
import os
import json


"""
python manage.py test apps.worldmap_connect.tests.WorldMapImporterTestCase.test_importer_rejects_bad_params_01
"""
from django.conf import settings

   
       
class WorldMapImporterTestCase(TestCase):
    

    def setUp(self):
        self.test_file_directory = join(dirname(realpath(__file__)), 'test_files')
       
    def get_worldmap_connecter_instance(self, timeout=None):
        worldmap_server_url = settings.WORLDMAP_SERVER_URL
        if timeout:
            return WorldMapImporter(timeout)
        else:
            return WorldMapImporter()
    
    def get_layer_test_params(self, fname):
        
        layer_params = {'title' : 'Boston Income'\
                , 'abstract' : 'Shapefile containing Boston, MA income levels from 19xx'\
                , 'email' : 'researcher@school.edu'\
                , 'shapefile_name' : fname\
                }
        return layer_params
    
    def get_file_fullpath(self, fname):
        return join(self.test_file_directory, fname)
    
    
    @unittest.skip('test_importer_rejects_bad_params_01')
    def test_importer_rejects_bad_params_01(self):
        """On the WorldMapImporter, check the function: send_shapefile_to_worldmap"""
        
        wmi = self.get_worldmap_connecter_instance()
        
        # Test params
        #
        fname = 'blah.zip'
        layer_params = self.get_layer_test_params(fname)

        # Try bad file path
        #
        msg = wmi.send_shapefile_to_worldmap(layer_params, fname)
        self.assertEqual(msg, {'message': 'This file does not exist: blah.zip', 'success': False})
        
        
        # Try with missing shapefile_name
        #
        layer_params.pop('shapefile_name')
        fname_fullpath = self.get_file_fullpath(fname)
        msg = wmi.send_shapefile_to_worldmap(layer_params, fname_fullpath)
        self.assertEqual(msg, {'message': "The following required keys were missing: ['shapefile_name']", 'success': False})

        # Test params missing email
        layer_params = self.get_layer_test_params(fname)
        layer_params.pop('email')
        msg = wmi.send_shapefile_to_worldmap(layer_params, fname_fullpath)
        print "error: [%s]" % msg
        self.assertEqual(msg, {'message': "The following required keys were missing: ['email']", 'success': False})

        # Test params missing title
        layer_params = self.get_layer_test_params(fname)
        layer_params.pop('title')
        msg = wmi.send_shapefile_to_worldmap(layer_params, fname_fullpath)
        self.assertEqual(msg, {'message': "The following required keys were missing: ['title']", 'success': False})
        
        
        # Test params missing abstract
        layer_params = self.get_layer_test_params(fname)
        layer_params.pop('abstract')
        msg = wmi.send_shapefile_to_worldmap(layer_params, fname_fullpath)
        self.assertEqual(msg, {'message': "The following required keys were missing: ['abstract']", 'success': False})
        
        # Test params missing title, abstract, email
        layer_params = self.get_layer_test_params(fname)
        layer_params.pop('title')
        layer_params.pop('abstract')
        layer_params.pop('email')
        msg = wmi.send_shapefile_to_worldmap(layer_params, fname_fullpath)
        self.assertEqual(msg, {'message': "The following required keys were missing: ['title', 'abstract', 'email']", 'success': False})
        
    
    def get_test_layer_params(self):
    
        test_data_file = join( dirname(abspath(__file__))\
                                    , 'fixtures'\
                                    , 'dataverse_info_test_fixtures_01.json'\
                                )
        if not isfile(test_data_file):
                raise ValueError('File not found: %s' % test_data_file)

        return json.loads(open(test_data_file, 'r').read())
    
    
    #@unittest.skip("Skip test that requires running WorldMap server")
    def test_timeout_exception(self):
        """
        These tests actually call the WorldMap API, e.g., a server has to be available
        """
        current_dir = os.path.dirname(os.path.realpath(__file__))
        f1 = os.path.join(current_dir, 'test_files', 'test_file01.txt')
        
        
        layer_params = self.get_test_layer_params()
        
        layer_params = dict(title = 'St Louis income 1990'\
                            , abstract = 'St. Louis data, long abstract regarding study, authors, etc. etc'\
                            , email = 'user@university.edu'\
                            , shapefile_name='test_file01.txt'\
                            )
        
        # Should reject a non .zip file
        #
        wmi = self.get_worldmap_connecter_instance()
        msg = wmi.send_shapefile_to_worldmap(layer_params, f1)

        err_msg = 'Unexpected error during upload: Saving is not implemented for extension .txt'
        self.assertEqual(msg['message'],  err_msg)
        self.assertEqual(msg['success'],  False)
        return
        #   Set request to 0.001 seconds to force timeout
        #
        f1 = os.path.join(self.test_file_directory, 'test_file01.zip')
        wmi = self.get_worldmap_connecter_instance(timeout=0.001)
        msg = wmi.send_shapefile_to_worldmap(title, abstract, f1, email)

        err_msg = 'This request timed out.  (Time limit: 0.001 seconds(s))'
        self.assertEqual(msg['message'],  err_msg)
        self.assertEqual(msg['success'],  False)
        
        
        #   Set .zip containing text file -- not a shapefile set
        #
        f1 = os.path.join(self.test_file_directory,  'test_file01.zip')
        wmi = self.get_worldmap_connecter_instance()
        msg = wmi.send_shapefile_to_worldmap(title, abstract, f1, email)
        
        #return
        err_msg_found1 = msg['message'].startswith('Unexpected error during upload: Expected helper file does not exist:')
        err_msg_found2 = msg['message'].endswith('a Shapefile requires helper files with the following extensions: [&#39;shx&#39;, &#39;shp&#39;, &#39;prj&#39;, &#39;dbf&#39;]')
                
        self.assertEqual(True, err_msg_found1)
        self.assertEqual(True, err_msg_found2)
        
        #   .zip contains correct shapefile set names -- but they are empty
        #
        f1 = os.path.join(self.test_file_directory,  'fail_shp.zip')
        wmi = self.get_worldmap_connecter_instance()
        msg = wmi.send_shapefile_to_worldmap(title, abstract, f1, email)
        
        err_msg_found3 = msg['message'].startswith('Unexpected error during upload: Could not save the layer')
        err_msg_found4 = msg['message'].endswith('there was an upload error: java.nio.BufferUnderflowException')

        self.assertEqual(True, err_msg_found3)
        self.assertEqual(True, err_msg_found4)
        self.assertEqual(False, msg['success'])
    

        