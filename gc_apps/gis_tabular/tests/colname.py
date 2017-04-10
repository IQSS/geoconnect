# -*- coding: utf-8 -*-
from django.test import TestCase
from django.template.defaultfilters import slugify
import re
# http://stackoverflow.com/questions/10589620/syntaxerror-non-ascii-character-xa3-in-file-when-function-returns-%C2%A3
import sys
reload(sys)
# http://stackoverflow.com/questions/21129020/how-to-fix-unicodedecodeerror-ascii-codec-cant-decode-byte
sys.setdefaultencoding('utf8')
from string import digits

"""
Run with:

python manage.py test gc_apps.gis_tabular.tests.colname
"""
class ColnameTest(TestCase):

    """
    Return a string that complies with the characters PostgreSQL allows as column names.
    Django's "slugify" does most of the work but we replace hyphens with underscores
    and strip leading digits. If the resulting string is empty, return a robotic but safe
    string based on the position of the column in the source data (i.e. "column_007").
    """
    def normalize_colname(self, colname, position):
        # The string returned must be a valid column name in PostgreSQL.
        # From https://www.postgresql.org/docs/9.6/static/sql-syntax-lexical.html#SQL-SYNTAX-IDENTIFIERS
        # "SQL identifiers and key words must begin with a letter (a-z, but also letters with diacritical marks and non-Latin letters) or an underscore (_). Subsequent characters in an identifier or key word can be letters, underscores, digits (0-9), or dollar signs ($). Note that dollar signs are not allowed in identifiers according to the letter of the SQL standard, so their use might render applications less portable. The SQL standard will not define a key word that contains digits or starts or ends with an underscore, so identifiers of this form are safe against possible conflict with future extensions of the standard."
        normalized = slugify(unicode(colname)).replace('-', '_').lstrip(digits)
        if (normalized == ''):
            # 7 becomes 007
            return 'column_' + '%03d' % position
        return normalized

    def test_colname_equals(self):
        self.assertEquals(self.normalize_colname('Police Stations', 1), 'police_stations')
        self.assertEquals(self.normalize_colname('Fire Hydrants', 1), 'fire_hydrants')
        # use generic name based on position passed in, zero-padded
        self.assertEquals(self.normalize_colname('()', 1), 'column_001')
        self.assertEquals(self.normalize_colname('!@#$%abc!@#$%', 1), 'abc')
        # change to ascii
        self.assertEquals(self.normalize_colname('MARK3QTÉ', 1), 'mark3qte')
        # strip leading digits
        self.assertEquals(self.normalize_colname('@13.LLIS_info_consistent', 1), 'llis_info_consistent')

    def test_colname_matches_regex(self):
        # pattern from http://stackoverflow.com/questions/4977898/check-for-valid-sql-column-name/4978062#4978062
        pattern = re.compile("^[a-zA-Z_][a-zA-Z0-9_]*$")
        self.assertTrue(pattern.match(self.normalize_colname('!@#$%abc!@#$%', 1)))
        self.assertTrue(pattern.match(self.normalize_colname('MARK3QTÉ', 1)))
        self.assertTrue(pattern.match(self.normalize_colname('@13.LLIS_info_consistent', 1)))
        iterateThroughFile = False
        # iterateThroughFile = True
        if (iterateThroughFile):
            # From Harvard Dataverse using 'SELECT name, label FROM datavariable;'
            with open ("/tmp/name.txt") as f:
            # with open ("/tmp/label.txt") as f:
                for line in f:
                    print "Testing line:", line
                    self.assertTrue(pattern.match(self.normalize_colname(line, 1)))
