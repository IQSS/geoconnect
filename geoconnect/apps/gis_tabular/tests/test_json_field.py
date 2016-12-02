from os.path import abspath, dirname, isfile, join, isdir
from unittest import skip

from django.test import TestCase

from geo_utils.json_field_reader import JSONHelper
from apps.gis_tabular.models import TestIt
from msg_util import *


class JSONFieldTester(TestCase):

    def setUp(self):
        pass
        #self.upload_california_census()
        #self.upload_mass_census()

    def tearDown(self):
        pass


    def test_1_dict(self):
        """Save data dict to JSONField, check type pre/post"""
        msgt(self.test_1_dict.__doc__)

        # attributes
        #
        tname = 'Obj 1'
        col_names_val = dict(a=1, b=2, c=3) #range(1,10)
        d = dict(name=tname,
                 column_names=col_names_val)

        # make object and save it
        #
        tunsaved = TestIt(**d)
        tunsaved.save()

        # Retrieve object
        #
        tsaved = TestIt.objects.first()

        print tsaved.column_names
        print type(tsaved.column_names)

        self.assertEqual(tsaved.column_names, col_names_val)
        self.assertEqual(tsaved.name, tname)

        #tsaved.delete()


    def test_2_string(self):
        """Save data string to JSONField, check type pre/post"""

        msgt(self.test_2_string.__doc__)

        #print TestIt.objects.count()

        # attributes
        #
        tname = 'Obj 1'
        col_names_val = 'ze string'
        d = dict(name=tname,
             column_names=col_names_val)

        # make object and save it
        #
        tunsaved = TestIt(**d)
        tunsaved.save()

        # Retrieve object
        #
        tsaved = TestIt.objects.first()

        print tsaved.column_names
        print type(tsaved.column_names)

        self.assertEqual(tsaved.column_names, col_names_val)
        self.assertEqual(tsaved.name, tname)

    def test_3_list(self):
        """Save data list to JSONField, check type pre/post"""

        msgt(self.test_3_list.__doc__)

        #print TestIt.objects.count()

        # attributes
        #
        tname = 'Obj 1'
        col_names_val = range(1,10)
        d = dict(name=tname,
             column_names=col_names_val)

        # make object and save it
        #
        tunsaved = TestIt(**d)
        tunsaved.save()

        # Retrieve object
        #
        tsaved = TestIt.objects.first()

        print tsaved.column_names
        print type(tsaved.column_names)

        self.assertEqual(tsaved.column_names, col_names_val)
        self.assertEqual(tsaved.name, tname)
