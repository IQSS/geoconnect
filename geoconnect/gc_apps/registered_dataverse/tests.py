from geo_utils.msg_util import *

from django.test import TestCase

from gc_apps.registered_dataverse.models import RegisteredDataverse
from gc_apps.registered_dataverse.registered_dataverse_helper import find_registered_dataverse

class RegisteredDataverseParseTest(TestCase):
    fixtures = ['testdata.json']

    def setUp(self):
        print 'set up'

    def find_existing_registered_dv(self, url_str):
        msgn('Looking for url: %s' % url_str)
        rd = find_registered_dataverse(url_str)
        self.assertTrue(rd is not None, 'URL not found: %s' % url_str)
        return rd
    
    def fail_to_find_existing_registered_dv(self, url_str):
        msgn('(should fail) Looking for url: %s' % url_str)
        rd = find_registered_dataverse(url_str)
        self.assertTrue(rd is None, 'URL should NOT be found: %s' % url_str)
        return rd
    
    def test_url_checks(self):

        #-------------------------------------------------
        msgn('check RegisteredDataverse count')
        #-------------------------------------------------
        self.assertEqual(RegisteredDataverse.objects.count(), 2, "Should be 2 RegisteredDataverse objects.  Found: %d" % RegisteredDataverse.objects.count())

        msgt('check urls')

        #-------------------------------------------------
        msgn('Find registered dataverse -- success cases')
        #-------------------------------------------------
        self.find_existing_registered_dv('https://dvn-build.hmdc.harvard.edu:443')
        self.find_existing_registered_dv('https://dvn-build.hmdc.harvard.edu:443/dataset.xhtml?globalId=doi:10.5072/FK2/R0KKEJ&versionId=33')
        self.find_existing_registered_dv('https://dvn-BUILD.HMDC.HArvard.edu:443/dataset.xhtml?globalId=doi:10.5072/FK2/R0KKEJ&versionId=33')
        self.find_existing_registered_dv('Https://Dvn-Build.Hmdc.Harvard.Edu:443/Dataset.Xhtml?Globalid=Doi:10.5072/Fk2/R0Kkej&Versionid=33')
        self.find_existing_registered_dv('HTTPS://DATAVERSE-DEMO.IQ.HARVARD.EDU:443/MY-MY-MY')
        rd = self.find_existing_registered_dv('https://dvn-build.hmdc.harvard.edu:443/?//id=what&a=mess?3globalId=doi:10.5072/FK2/R0KKEJ&versionId=33')


        #-------------------------------------------------
        msgn('Deactive RegisteredDataverse and try to retrieve it.')
        #-------------------------------------------------
        rd.active = False
        rd.save()
        rd2 = find_registered_dataverse('https://dvn-build.hmdc.harvard.edu:443')
        self.assertTrue(rd2 is None)
        
        rd.active = True
        rd.save()
        self.find_existing_registered_dv('https://dvn-build.hmdc.harvard.edu:443')
        
        
        #-------------------------------------------------
        msgn('Find registered dataverse -- fail cases')
        #-------------------------------------------------
        self.fail_to_find_existing_registered_dv('hullo')
        self.fail_to_find_existing_registered_dv('dvn-build.hmdc.harvard.edu:443')
        self.fail_to_find_existing_registered_dv('http://dvn-build.hmdc.harvard.edu:443')   # not https
        
        
        