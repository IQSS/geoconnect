from django.test import TestCase
from django.template.defaultfilters import slugify
import re

"""
Run with:

python manage.py test gc_apps.gis_tabular.tests.colname
"""
class ColnameTest(TestCase):

    def normalize_colname(self, colname, position):
        # The string returned must be a valid column name in PostgreSQL.
        # From https://www.postgresql.org/docs/9.6/static/sql-syntax-lexical.html#SQL-SYNTAX-IDENTIFIERS
        # "SQL identifiers and key words must begin with a letter (a-z, but also letters with diacritical marks and non-Latin letters) or an underscore (_). Subsequent characters in an identifier or key word can be letters, underscores, digits (0-9), or dollar signs ($). Note that dollar signs are not allowed in identifiers according to the letter of the SQL standard, so their use might render applications less portable. The SQL standard will not define a key word that contains digits or starts or ends with an underscore, so identifiers of this form are safe against possible conflict with future extensions of the standard."
        slugified = slugify(unicode(colname)).replace('-', '_')
        if (slugified == ''):
            return 'column_' + '%03d' % position
        # FIXME: Make this more robust per https://github.com/IQSS/dataverse/issues/3489
        return slugified

    def test_colname_equals(self):
        self.assertEquals(self.normalize_colname('Police Stations', 1), 'police_stations')
        self.assertEquals(self.normalize_colname('Fire Hydrants', 1), 'fire_hydrants')
        self.assertEquals(self.normalize_colname('()', 1), 'column_001')
        self.assertEquals(self.normalize_colname('!@#$%abc!@#$%', 1), 'abc')

    def test_colname_matches_regex(self):
        # pattern from http://stackoverflow.com/questions/4977898/check-for-valid-sql-column-name/4978062#4978062
        pattern = re.compile("^[a-zA-Z_][a-zA-Z0-9_]*$")
        # FIXME: Add more test cases based on production data.
        self.assertTrue(pattern.match(self.normalize_colname('!@#$%abc!@#$%', 1)))
