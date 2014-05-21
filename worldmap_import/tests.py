import unittest
from django.test import TestCase
from worldmap_importer import WorldMapImporter
from StringIO import StringIO
import os

try:
    from test_token import WORLDMAP_SERVER_URL
except:
    WORLDMAP_SERVER_URL = 'http://worldmap-fake-url.harvard.edu'
       
class WorldMapImporterTestCase(TestCase):
    def setUp(self):
        pass
        #Animal.objects.create(name="lion", sound="roar")
        #Animal.objects.create(name="cat", sound="meow")

    def get_worldmap_importer_instance(self, timeout=None):
        worldmap_server_url = WORLDMAP_SERVER_URL
        if timeout:
            return WorldMapImporter(worldmap_server_url, timeout)
        else:
            return WorldMapImporter(worldmap_server_url)
    
    def get_layer_test_params(self, fname):
        layer_params = {'title' : 'Boston Income'\
                , 'abstract' : 'Shapefile containing Boston, MA income levels from 19xx'\
                , 'email' : 'researcher@school.edu'\
                , 'shapefile_name' : fname\
                }
        return layer_params
        
    def test_importer_rejects_bad_params_01(self):
        """On the WorldMapImporter, check the function: send_shapefile_to_worldmap"""
        #python manage.py test worldmap_import.tests.WorldMapImporterTestCase.test_importer_rejects_bad_params_01
        fname = 'blah.zip'
        
        
        wmi = self.get_worldmap_importer_instance()
        
        # Test params missing shapefile_name
        layer_params = self.get_layer_test_params(fname)
        layer_params.pop('shapefile_name')
        msg = wmi.send_shapefile_to_worldmap(layer_params, fname)
        self.assertEqual(msg, {'message': 'These parameters are missing from "layer_params": shapefile_name', 'success': False})
        
        # Test params missing email
        layer_params = self.get_layer_test_params(fname)
        layer_params.pop('email')
        msg = wmi.send_shapefile_to_worldmap(layer_params, fname)
        self.assertEqual(msg, {'message': 'These parameters are missing from "layer_params": email', 'success': False})

        # Test params missing title
        layer_params = self.get_layer_test_params(fname)
        layer_params.pop('title')
        msg = wmi.send_shapefile_to_worldmap(layer_params, fname)
        self.assertEqual(msg, {'message': 'These parameters are missing from "layer_params": title', 'success': False})
        
        # Test params missing abstract
        layer_params = self.get_layer_test_params(fname)
        layer_params.pop('abstract')
        msg = wmi.send_shapefile_to_worldmap(layer_params, fname)
        self.assertEqual(msg, {'message': 'These parameters are missing from "layer_params": abstract', 'success': False})
        
        # Test params missing title, abstract, email
        layer_params = self.get_layer_test_params(fname)
        layer_params.pop('title')
        layer_params.pop('abstract')
        layer_params.pop('email')
        msg = wmi.send_shapefile_to_worldmap(layer_params, fname)
        self.assertEqual(msg, {'message': 'These parameters are missing from "layer_params": title, abstract, email', 'success': False})
        
        
    
        
    def test_importer_rejects_bad_params_02(self):
        """On the WorldMapImporter, check the function: send_shapefile_to_worldmap2"""
        
        f1 = 'blah.zip'
        title = 'St Louis income 1990'
        email = 'user@university.edu'
        abstract = 'St. Louis data, long abstract regarding study, authors, etc. etc'
        
        wmi = self.get_worldmap_importer_instance()

        # Test no title 1
        msg = wmi.send_shapefile_to_worldmap2(None, abstract, f1, email)
        self.assertEqual(msg, {'message': 'A title is required', 'success': False})

        # Test no title 2
        msg = wmi.send_shapefile_to_worldmap2('  ', abstract, f1, email)
        self.assertEqual(msg, {'message': 'A title is required', 'success': False})
        #self.assertEqual(cat.speak(), 'The cat says "meow"')

        # Test no abstract 1
        msg = wmi.send_shapefile_to_worldmap2(title, None, f1, email)
        self.assertEqual(msg, {'message': 'An abstract is required', 'success': False})

        # Test no abstract 2
        msg = wmi.send_shapefile_to_worldmap2(title, ' ', f1, email)
        self.assertEqual(msg, {'message': 'An abstract is required', 'success': False})

        # Test no email
        msg = wmi.send_shapefile_to_worldmap2(title, abstract, f1, email='')
        self.assertEqual(msg, {'message': 'An email is required', 'success': False})
    
    def test_importer_rejects_nonexistent_file(self):
        f1 = 'test-shape-file-blah.zip'
        title = 'St Louis income 1990'
        abstract = 'St. Louis data, long abstract regarding study, authors, etc. etc'
        email = 'user@university.edu'
        
        wmi = self.get_worldmap_importer_instance()
        
        msg = wmi.send_shapefile_to_worldmap2(title, abstract, f1, email)
        self.assertEqual(msg,  {'message': 'This file does not exist: test-shape-file-blah.zip', 'success': False})
 
    @unittest.skip("Skip test that requires running WorldMap server")
    def test_timeout_exception(self):
        """
        These tests actually call the WorldMap API, e.g., a server has to be available
        """
        current_dir = os.path.dirname(os.path.realpath(__file__))
        f1 = os.path.join(current_dir, 'test_file', 'test_file01.txt')
        title = 'St Louis income 1990'
        abstract = 'St. Louis data, long abstract regarding study, authors, etc. etc'
        email = 'user@university.edu'
        
        # Should reject a non .zip file
        #
        wmi = self.get_worldmap_importer_instance()
        msg = wmi.send_shapefile_to_worldmap2(title, abstract, f1, email)
        self.assertEqual(msg,  {u'errormsgs': [u'Unexpected error during upload: Saving is not implemented for extension .txt'], u'success': False})
       
        #   Set request to 0.001 seconds to force timeout
        #
        f1 = os.path.join(current_dir, 'test_file', 'test_file01.zip')
        wmi = self.get_worldmap_importer_instance(timeout=0.001)
        msg = wmi.send_shapefile_to_worldmap2(title, abstract, f1, email)
        self.assertEqual(msg, {'message': 'This request timed out.  (Time limit: 0.001 seconds(s))', 'success': False})
        
        #   Set .zip containing text file -- not a shapefile set
        #
        f1 = os.path.join(current_dir, 'test_file', 'test_file01.zip')
        wmi = self.get_worldmap_importer_instance()
        msg = wmi.send_shapefile_to_worldmap2(title, abstract, f1, email)
        #print msg['errormsgs']
        #return
        err_msg_found1 = msg['errormsgs'][0].startswith('Unexpected error during upload: Expected helper file does not exist:')
        err_msg_found2 = msg['errormsgs'][0].endswith('a Shapefile requires helper files with the following extensions: [&#39;shx&#39;, &#39;shp&#39;, &#39;prj&#39;, &#39;dbf&#39;]')
        
        self.assertEqual(True, err_msg_found1)
        self.assertEqual(True, err_msg_found2)
        
        #   .zip contains correct shapefile set names -- but they are empty
        #
        f1 = os.path.join(current_dir, 'test_file', 'fail_shp.zip')
        wmi = self.get_worldmap_importer_instance()
        msg = wmi.send_shapefile_to_worldmap2(title, abstract, f1, email)
        #print msg['errormsgs']
        #return
        
        err_msg_found3 = msg['errormsgs'][0].startswith('Unexpected error during upload: Could not save the layer')
        err_msg_found4 = msg['errormsgs'][0].endswith('there was an upload error: java.nio.BufferUnderflowException')

        self.assertEqual(True, err_msg_found3)
        self.assertEqual(True, err_msg_found4)
    

        