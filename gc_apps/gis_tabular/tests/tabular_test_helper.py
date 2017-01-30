"""
For developing tabular api
"""

from os.path import realpath, dirname, isfile, join, isdir
import sys
import json
import requests


from msg_util import *


"""
Load up the server and username
"""
GEONODE_CREDS_FNAME = join(dirname(realpath(__file__)), 'server_credentials.json')
assert isfile(GEONODE_CREDS_FNAME), 'Server credentials file not found: %s' % GEONODE_CREDS_FNAME
try:
    GEONODE_CREDS_JSON = json.loads(open(GEONODE_CREDS_FNAME, 'r').read())
except Exception as e:
    raise Exception('Could not parse tabular credentials JSON file: %s\n%s' % (GEONODE_CREDS_FNAME, str(e)))
    
'''
logger.error(
"Error Creating table %s:%s",
instance.name,
)
'''

GEONODE_SERVER = GEONODE_CREDS_JSON['SERVER_URL']
GEONODE_USERNAME = GEONODE_CREDS_JSON['USERNAME']
GEONODE_PASSWORD = GEONODE_CREDS_JSON['PASSWORD']

INPUT_DIR = join(dirname(realpath(__file__)), 'input')


class TabularTest:
    
    def __init__(self, base_url=GEONODE_SERVER, username=GEONODE_USERNAME, pw=GEONODE_PASSWORD):
        self.client = requests.session()
        self.base_url = base_url

        self.geonode_username = username
        self.geonode_password = pw
        
        self.login_url =  self.base_url + "/accounts/login/"
        self.datatable_upload_url  = self.base_url + '/datatables/api/upload'
        self.shp_layer_upload_url = self.base_url + '/layers/upload'
        
        self.join_datatable_url = self.base_url + '/datatables/api/join'
        self.upload_and_join_url = self.base_url + '/datatables/api/upload_and_join'
                
        self.delete_datatable_url = self.base_url + '/datatables/api/**dt_id**/remove'
        
        #self.datatable_name = None
        
        
    def get_delete_datatable_url(self, datatable_id):
        assert datatable_id is not None, 'datatable_id cannot be None'
        
        return '%s/datatables/api/%s/remove' % (self.base_url, datatable_id)
        
        
    def login_for_cookie(self):

        msgt('login_for_cookie: %s' % self.login_url)

        # Retrieve the CSRF token first
        self.client.get(self.login_url)  # sets the cookie
        csrftoken = self.client.cookies['csrftoken']

        login_data = dict(username=self.geonode_username\
                        , password=self.geonode_password\
                        , csrfmiddlewaretoken=csrftoken\
                        )
        r = self.client.post(self.login_url, data=login_data, headers={"Referer": "test-client"})

        #print r.text
        print r.status_code

        
    def upload_datatable_file(self, title, fname_to_upload):

        msgt('upload_datatable_file: %s' % self.datatable_upload_url)

        files = {'uploaded_file': open(fname_to_upload,'rb')}
        response = self.client.post(self.datatable_upload_url\
                    , data={'title' : title }\
                    , files=files)

        msg(response.text)
        msg(response.status_code)
        resp_dict = json.loads(response.content)
        datatable_name = resp_dict['datatable_name']
        print datatable_name
        return resp_dict

    
    def delete_datatable(self, datatable_id):
        msgt('delete_datatable: %s' % datatable_id)
        
        assert datatable_id is not None, "datatable_id cannot be None"
        
        api_url = self.get_delete_datatable_url(datatable_id)
        
        response = self.client.get(api_url)
        msg(response.text)
        msg(response.status_code)
        
        resp_dict = json.loads(response.content)
        return resp_dict
        
        """
        csrftoken = self.client.cookies['csrftoken']

        login_data = dict(username=self.geonode_username\
                        , password=self.geonode_password\
                        , csrfmiddlewaretoken=csrftoken\
                        )
        r = self.client.post(self.login_url, data=login_data, headers={"Referer": "test-client"})
        """

    def upload_and_join(self, fname_to_upload, join_props):
        msgt('upload_and_join: %s %s' % (fname_to_upload, join_props))

        assert isfile(fname_to_upload), "File to upload not found: %s" % fname_to_upload
        assert hasattr(join_props, 'has_key')\
            , "join_props should be a dictionary type of object.  Found: %s" % join_props.__class__.__name
        

        files = {'uploaded_file': open(fname_to_upload,'rb')}

        r = self.client.post(self.upload_and_join_url\
                                , data=join_props\
                                , files=files\
                                )

        print r.content
        if r.status_code == 200:
            try:
                return json.loads(r.content)
            except:
                msg(r.content)
                msgx('Failed to load content as JSON: %s' % sys.exc_info()[0])
        
        msg(r.content)
        msg(r.status_code)
        return None
        
                  
    def add_shapefile_layer(self, shp_dirname, shp_fname_prefix):


        msgt('add_shapefile_layer: %s' % self.shp_layer_upload_url)

        required_shapefile_extensions = dict(base_file='shp'\
                                        , dbf_file='dbf'\
                                        , prj_file='prj'\
                                        , shx_file='shx'\
                                        )
        extra_shapefile_extensions = dict(xml_file='xml')
        
        files = {}
        
        # Add required files to request.   
        #
        for name, shp_ext in required_shapefile_extensions.items():
            fullname = join(shp_dirname, '%s.%s' % (shp_fname_prefix, shp_ext))
            assert isfile(fullname), "Part of shapefile not found: %s" % fullname
        
            files[name] = open(fullname, 'rb')
            
        # If available, add additional files to request.   
        #
        for name, shp_ext in extra_shapefile_extensions.items():
            fullname = join(shp_dirname, '%s.%s' % (shp_fname_prefix, shp_ext))
            if isfile(fullname):
                files[name] = open(fullname, 'rb')

        
        msg(files)
        """
        files = {
            'base_file': open(join(shp_dirname, '%s.shp' % shp_fname_prefix), 'rb'),
            'dbf_file': open(join(shp_dirname, '%s.dbf' % shp_fname_prefix), 'rb'),
            'prj_file': open(join(shp_dirname, '%s.prj' % shp_fname_prefix), 'rb'),
            'shx_file': open(join(shp_dirname, '%s.shx' % shp_fname_prefix), 'rb'),
            }
        """

        #     'base_file': open('scratch/tl_2013_06_tract.shp','rb'),
        #    'dbf_file': open('scratch/tl_2013_06_tract.dbf','rb'),
        #    'prj_file': open('scratch/tl_2013_06_tract.prj','rb'),
        #    'shx_file': open('scratch/tl_2013_06_tract.shx','rb'),
        #    'xml_file': open('scratch/tl_2013_06_tract.shp.xml','rb')

        # Retrieve the CSRF token first
        #self.client.get()  # sets the cookie
    
        csrftoken = self.client.cookies['csrftoken']
        perms = '{"users":{"AnonymousUser":["view_resourcebase","download_resourcebase"]},"groups":{}}'

        response = self.client.post(self.shp_layer_upload_url\
                        , files=files\
                        , data={'csrfmiddlewaretoken':csrftoken\
                                    , 'permissions':perms\
                                }\
                        )

        print response.content
        new_layer_name = json.loads(response.content)['url'].split('/')[2].replace('%3A', ':')
        print new_layer_name
        
    def join_datatable_to_layer(self, join_props):
        """        
        Join a layer to a csv data table.  Example:
        
            join_props = {
                'table_name': 'ca_tracts_pop_002',
                'table_attribute': 'GEO.id2',
                'layer_typename': 'geonode:tl_2013_06_tract',
                'layer_attribute': 'GEOID'
            }
        """
        msgt('join_datatable_to_layer: %s' % self.join_datatable_url)
        
        assert isinstance(join_props, dict), "join_props must be a dict {}"
        for k in ('table_name', 'table_attribute', 'layer_typename', 'layer_attribute'):
            assert join_props.has_key(k), "join_props is missing key: %s" % k
         
       
        msg(join_props)

        response = self.client.post(self.join_datatable_url, data=join_props)
        print response.content
        
        
        
if __name__=='__main__':
    tr = TestRun()
    tr.login_for_cookie()
    
    # Upload CSV
    title = 'California Pop Test'
    fname_to_upload = join(INPUT_DIR, 'ca_tracts_pop_002.csv')
    #tr.upload_datatable_file(title, fname_to_upload)
    # {"datatable_id": 28, "datatable_name": "ca_tracts_pop_002"}
    
    # Join CSV to existing layer
    tr.upload_three('---', '----')
    # {'layer_typename': 'geonode:tl_2013_06_tract', 'table_name': 'ca_tracts_pop_002', 'table_attribute': 'GEO.id2', 'layer_attribute': 'GEOID'}
    #{"join_layer": "geonode:view_join_tl_2013_06_tract_ca_tracts_pop_002", "source_layer": "geonode:tl_2013_06_tract", "view_name": "view_join_tl_2013_06_tract_ca_tracts_pop_002", "table_attribute": "GEO.id2", "layer_attribute": "GEOID", "layer_url": "/layers/geonode%3Aview_join_tl_2013_06_tract_ca_tracts_pop_002", "datatable": "ca_tracts_pop_002", "join_id": 8}
    #tr.add_shapefile_layer('social_disorder_in_boston_yqh_zip_411')
    
    
    #tr.upload_three('social_disorder_in_boston_yqh_zip_411', 'geonode:c_bra_bl')
    
"""
National zip codes:
    - tl_2014_us_zcta510.zip

"""