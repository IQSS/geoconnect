# -*- coding: utf-8 -*-
import re
import sys
from django.test import TestCase
from gc_apps.geo_utils.tabular_util import normalize_colname
# http://stackoverflow.com/questions/10589620/syntaxerror-non-ascii-character-xa3-in-file-when-function-returns-%C2%A3
reload(sys)
# http://stackoverflow.com/questions/21129020/how-to-fix-unicodedecodeerror-ascii-codec-cant-decode-byte
sys.setdefaultencoding('utf8')

"""
Run with:

python manage.py test gc_apps.gis_tabular.tests.colname
"""
class ColnameTest(TestCase):

    def test_colname_equals(self):
        self.assertEquals(normalize_colname('Police Stations', 1), 'police_stations')
        self.assertEquals(normalize_colname('Fire Hydrants', 1), 'fire_hydrants')
        # use generic name based on position passed in, zero-padded
        self.assertEquals(normalize_colname('()', 1), 'column_001')
        self.assertEquals(normalize_colname('!@#$%abc!@#$%', 1), 'abc')
        # change to ascii
        self.assertEquals(normalize_colname('MARK3QTÉ', 1), 'mark3qte')
        # strip leading digits
        self.assertEquals(normalize_colname('@13.LLIS_info_consistent', 1), 'llis_info_consistent')

    def test_colname_matches_regex(self):
        # pattern from http://stackoverflow.com/questions/4977898/check-for-valid-sql-column-name/4978062#4978062
        pattern = re.compile("^[a-zA-Z_][a-zA-Z0-9_]*$")
        self.assertTrue(pattern.match(normalize_colname('!@#$%abc!@#$%', 1)))
        self.assertTrue(pattern.match(normalize_colname('MARK3QTÉ', 1)))
        self.assertTrue(pattern.match(normalize_colname('@13.LLIS_info_consistent', 1)))
        iterateThroughFile = False
        # iterateThroughFile = True
        if (iterateThroughFile):
            # From Harvard Dataverse using 'SELECT name, label FROM datavariable;'
            with open ("/tmp/name.txt") as f:
            # with open ("/tmp/label.txt") as f:
                for line in f:
                    print "Testing line:", line
                    self.assertTrue(pattern.match(normalize_colname(line, 1)))
