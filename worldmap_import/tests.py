from django.test import TestCase
from worldmap_importer import WorldMapImporter

class WorldMapImporterTestCase(TestCase):
    def setUp(self):
        pass
        #Animal.objects.create(name="lion", sound="roar")
        #Animal.objects.create(name="cat", sound="meow")

    def test_importer_rejects_bad_params(self):
        """Animals that can speak are correctly identified"""
        f1 = '../scripts/worldmap_api/test_shps/blah.zip'
        title = 'St Louis income 1990'
        abstract = 'St. Louis data, long abstract regarding study, authors, etc. etc'
        
        wmi = WorldMapImporter()
        msg = wmi.send_shapefile_to_worldmap2(title, abstract, f1)
        self.assertEqual(msg, {'message': 'This file does not exist: ../scripts/worldmap_api/test_shps/blah.zip', 'success': False})

        # Test no title 1
        msg = wmi.send_shapefile_to_worldmap2(None, abstract, f1)
        self.assertEqual(msg, {'message': 'A title is required', 'success': False})

        # Test no title 2
        msg = wmi.send_shapefile_to_worldmap2('  ', abstract, f1)
        self.assertEqual(msg, {'message': 'A title is required', 'success': False})
        #self.assertEqual(cat.speak(), 'The cat says "meow"')

        # Test no abstract 1
        msg = wmi.send_shapefile_to_worldmap2(title, None, f1)
        self.assertEqual(msg, {'message': 'An abstract is required', 'success': False})

        # Test no abstract 2
        msg = wmi.send_shapefile_to_worldmap2(title, ' ', f1)
        self.assertEqual(msg, {'message': 'An abstract is required', 'success': False})
        