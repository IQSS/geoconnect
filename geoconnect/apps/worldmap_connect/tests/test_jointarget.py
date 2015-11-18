from django.utils import timezone
from django.test import TestCase

from apps.worldmap_connect.models import JoinTargetInformation

class JoinTargetInformationTestCase(TestCase):
    """
    Test basic params
    """

    def setUp(self):

        jt_name = 'tcase-{0}'.format(timezone.now().strftime("%Y-%m-%d %H:%M:%S"))
        jt = JoinTargetInformation(name=jt_name,
            target_info={u'data': [{u'layer': u'geonode:massachusetts_census_nhu', u'geocode_type_slug': u'us-census-tract', u'geocode_type': u'US Census Tract', u'attribute': {u'attribute': u'TRACTCE', u'type': u'xsd:string'}, u'year': 2010, u'type': None, u'id': 3}], u'success': True})
        jt.save()

    def test_join_target_formatter(self):
        """Test formattter"""

        # Retrieve the test JoinTargetInformation objects
        #
        join_target_info = JoinTargetInformation.objects.first()

        print 'join_target_info', join_target_info
        # Test "get_geocode_types()"
        #
        geocode_types = join_target_info.get_geocode_types()
        print 'geocode_types', geocode_types
        self.assertEqual(geocode_types, [('US Census Tract', 'us-census-tract')])

        # Test "get_join_targets_by_type(--geocode type or None--)"
        #
        jtargets_by_type = join_target_info.get_join_targets_by_type('us-census-tract')
        print 'jtargets_by_type', jtargets_by_type
        self.assertEqual(jtargets_by_type, [('US Census Tract (2010)', 3)])
        #self.assertEqual(cat.speak(), 'The cat says "meow"')

"""
python manage.py shell
from apps.worldmap_connect.utils import get_latest_jointarget_information
from apps.worldmap_connect.jointarget_formatter import JoinTargetFormatter

jt = get_latest_jointarget_information()
jt.target_info

fmt = JoinTargetFormatter(jt.target_info)
fmt.get_geocode_types()
"""
