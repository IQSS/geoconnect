from os.path import join, dirname
import json

from django.utils import timezone
from django.test import TestCase
from django.core import management

from apps.worldmap_connect.models import JoinTargetInformation
from apps.worldmap_connect.single_join_target_info import SingleJoinTargetInfo
from geo_utils.msg_util import msgt, msg

JOIN_TARGETS_FILENAME = join(dirname(__file__), 'input', 'jointargets_2016-1202.json')

class JoinTargetInformationTestCase(TestCase):
    """
    Test basic params
    """

    def setUp(self):
        print ('load fixtures')
        json_data = open(JOIN_TARGETS_FILENAME, 'r').read()
        self.join_targets_json = json.loads(json_data)

    def test_target_read_functions(self):
        """Check expected format type functions including:
        - is_target_column_string()
        - requires_zero_padding()
        - get_zero_pad_length()
        - does_join_column_potentially_need_formatting()
        """
        msgt(self.test_target_read_functions.__doc__)


        j = JoinTargetInformation(name='test', target_info=self.join_targets_json)
        j.save()

        self.assertEqual(type(j.target_info), dict)

        cnt = 0
        for info in j.target_info['data']:
            target_info = SingleJoinTargetInfo(info)
            cnt += 1
            #target_info.show()
            if target_info.target_layer_name == 'geonode:census_tracts_2010_boston_6f6':
                msg('a) checking target: %s' % (target_info.target_layer_name))
                self.assertEqual(target_info.is_target_column_string(), True)
                self.assertEqual(target_info.does_join_column_potentially_need_formatting(), True)
            elif target_info.target_layer_name == 'geonode:us_zip_code_2015_boston_v3q':
                msg('b) checking target: %s' % (target_info.target_layer_name))
                self.assertEqual(target_info.is_target_column_string(), True)
                self.assertEqual(target_info.requires_zero_padding(), True)
                self.assertEqual(target_info.get_zero_pad_length(), 5)
                self.assertEqual(target_info.does_join_column_potentially_need_formatting(), True)
            elif target_info.target_id == 19:
                msg('c) checking target: %s' % (target_info.target_layer_name))
                self.assertEqual(target_info.is_target_column_string(), False)
                self.assertEqual(target_info.requires_zero_padding(), False)
                self.assertEqual(target_info.get_zero_pad_length(), None)
                self.assertEqual(target_info.does_join_column_potentially_need_formatting(), False)



    def xtest_join_target_formatter(self):
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
jt_name = 'tcase-{0}'.format(timezone.now().strftime("%Y-%m-%d %H:%M:%S"))
jt = JoinTargetInformation(name=jt_name,
    target_info={u'data': [{u'layer': u'geonode:massachusetts_census_nhu', u'geocode_type_slug': u'us-census-tract', u'geocode_type': u'US Census Tract', u'attribute': {u'attribute': u'TRACTCE', u'type': u'xsd:string'}, u'year': 2010, u'type': None, u'id': 3}], u'success': True})
jt.save()
"""
"""
python manage.py shell
from apps.worldmap_connect.utils import get_latest_jointarget_information
from apps.worldmap_connect.jointarget_formatter import JoinTargetFormatter

jt = get_latest_jointarget_information()
jt.target_info

fmt = JoinTargetFormatter(jt.target_info)
fmt.get_geocode_types()
"""
