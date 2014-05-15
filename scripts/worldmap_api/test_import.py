import itertools
import mimetools
import mimetypes
from cStringIO import StringIO
import urllib
import urllib2
import json
#import cookielib
"""
Use this view:
https://github.com/mbertrand/cga-worldmap/blob/dvn/geonode/dvn/views.py

Token
https://github.com/mbertrand/cga-worldmap/blob/dvn/geonode/settings/base.py

"""
DVN_TOKEN = "JdPGVSga9yM8gt74ZpLp"
             
URL_BASE = 'http://107.22.231.227/dvn/import'

def test_worldmap_import():
    params = {'title' : 'Boston Income'\
            , 'abstract' : '[test] Shapefile containing Boston, MA income levels from 19xx'\
            , 'email' : 'raman_prasad@harvard.edu'\
            , 'shapefile_name' : 'income_in_boston_gui.zip'\
            , 'geoconnect_token' : DVN_TOKEN\
            }
    print json.dumps(params)
    
    shp_filename = 'test_shps/income_in_boston_gui.zip'

    request = urllib2.Request(URL_BASE)
    request.get_method = lambda:'POST'  # GET, POST, DELETE
    request.add_data(urllib.urlencode(params))
    print 'Request method after data :', request.get_method()
    print
    print 'OUTGOING DATA:'
    print request.get_data()

    print
    print 'SERVER RESPONSE:'
    print urllib2.urlopen(request).read()
    response = urllib2.urlopen(request)

    print response.info()
    #print response.read()
    """
    query_args = { 'q':'query string', 'foo':'bar' }
    encoded_args = urllib.urlencode(query_args)
    url = 'http://localhost:8080/'
    print urllib2.urlopen(url, encoded_args).read()
    """
if __name__=='__main__':
    test_worldmap_import()
#print response.info()    
#print response.read()
