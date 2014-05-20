# from http://pymotw.com/2/urllib2/
import itertools
import mimetypes
import mimetools

from cStringIO import StringIO
import urllib
import urllib2
import json

import os
import timeit

from test_token import DVN_TOKEN

class MultiPartForm(object):
    """Accumulate the data to be used when posting a form."""

    def __init__(self):
        self.form_fields = []
        self.files = []
        self.boundary = mimetools.choose_boundary()
        return
    
    def get_content_type(self):
        return 'multipart/form-data; boundary=%s' % self.boundary

    def add_field(self, name, value):
        """Add a simple field to the form data."""
        self.form_fields.append((name, value))
        return

    def add_file(self, fieldname, filename, fileHandle, mimetype=None):
        """Add a file to be uploaded."""
        body = fileHandle.read()
        if mimetype is None:
            mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        self.files.append((fieldname, filename, mimetype, body))
        return
    
    def __str__(self):
        """Return a string representing the form data, including attached files."""
        # Build a list of lists, each containing "lines" of the
        # request.  Each part is separated by a boundary string.
        # Once the list is built, return a string where each
        # line is separated by '\r\n'.  
        parts = []
        part_boundary = '--' + self.boundary
        
        # Add the form fields
        parts.extend(
            [ part_boundary,
              'Content-Disposition: form-data; name="%s"' % name,
              '',
              value,
            ]
            for name, value in self.form_fields
            )
        
        # Add the files to upload
        parts.extend(
            [ part_boundary,
              'Content-Disposition: file; name="%s"; filename="%s"' % \
                 (field_name, filename),
              'Content-Type: %s' % content_type,
              '',
              body,
            ]
            for field_name, filename, content_type, body in self.files
            )
        
        # Flatten the list and add closing boundary marker,
        # then return CR+LF separated data
        flattened = list(itertools.chain(*parts))
        flattened.append('--' + self.boundary + '--')
        flattened.append('')
        return '\r\n'.join(flattened)

def load_test_file(params): 
    form = MultiPartForm()
    for k, v in params.iteritems():
        form.add_field(k, v)
        #form.add_field('lastname', 'Hellmann')
    
    # Add a file
    #fcontent = open('test_shps/income_in_boston_gui.zip', 'r').read()
    #fcontent = open('test_shps/TheFinger.zip', 'r').read()
    fcontent = open(os.path.join('test_shps', params['shapefile_name']), 'r').read()
    
    form.add_file('content', params['shapefile_name'], fileHandle=StringIO(fcontent))

    # Build the request
    URL_BASE = 'http://107.22.231.227/dvn/import'
    request = urllib2.Request(URL_BASE)#'http://localhost:8080/')
    #request.add_header('User-agent', 'OpenAnything/1.0 +http://diveintopython.org/')
    body = str(form)
    request.add_header('Content-type', form.get_content_type())
    request.add_header('Content-length', len(body))
    request.add_data(body)

    print
    print 'OUTGOING DATA:'
    print request.get_data()

    print
    print 'SERVER RESPONSE:'
    content = urllib2.urlopen(request).read()
    print 'content [%s]' % content

params1 = {'title' : 'Boston Income'\
        , 'abstract' : '[test] Shapefile containing Boston, MA income levels from 19xx'\
        , 'email' : 'raman_prasad@harvard.edu'\
        , 'shapefile_name' : 'income_in_boston_gui.zip'\
        , 'geoconnect_token' : DVN_TOKEN\
        }

params2 = {'title' : 'Boston Geo Infrastructure Addresses'\
        , 'abstract' : '[test] Shapefile .dbf is 435mb when unzipped'\
        , 'email' : 'raman_prasad@harvard.edu'\
        , 'shapefile_name' : 'Addresses.zip'\
        , 'geoconnect_token' : DVN_TOKEN\
        }

params3 = {'title' : 'Social Disorder in Boston'\
        , 'abstract' : '[test] Shapefile .dbf is 2.6mb when unzipped'\
        , 'email' : 'raman_prasad@harvard.edu'\
        , 'shapefile_name' : 'social_disorder_in_boston.zip'\
        , 'geoconnect_token' : DVN_TOKEN\
        }
        
if __name__=='__main__':

    #load_test_file(params1)
    
    print(timeit.timeit("load_test_file(params1)", setup="from __main__ import load_test_file, params1", number=1))

"""
-------------------------------------
SERVER RESPONSE for params1
-------------------------------------
^[[?1;2c^[[?1;2c^[[?1;2c^[[?1;2c{"layer_link": "http://107.22.231.227/data/geonode:income_in_boston_gui_zip_xq3", "worldmap_username": "raman_prasad", "layer_name": "geonode:income_in_boston_gui_zip_xq3", "success": true, "embed_map_link": "http://107.22.231.227/maps/embed?layers=geonode:income_in_boston_gui_zip_xq3"}
-------------------------------------
s: 2.47385692596

-------------------------------------
SERVER RESPONSE for params3
-------------------------------------
{"layer_link": "http://107.22.231.227/data/geonode:social_disorder_in_boston_zip_i87", "worldmap_username": "raman_prasad", "layer_name": "geonode:social_disorder_in_boston_zip_i87", "success": true, "embed_map_link": "http://107.22.231.227/maps/embed/?layers=geonode:social_disorder_in_boston_zip_i87"}
-------------------------------------
s: 3.23020100594

"""


"""{"layer_link": "http://107.22.231.227/data/geonode:income_in_boston_gui_zip_10e"
, "worldmap_username": "raman_prasad"
, "layer_name": "geonode:income_in_boston_gui_zip_10e"
, "success": true
, "embed_map_link": "http://107.22.231.227/maps/embed?layers=geonode:income_in_boston_gui_zip_10e"}
"""