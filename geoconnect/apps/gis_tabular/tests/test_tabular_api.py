from os.path import abspath, dirname, isfile, join, isdir
from msg_util import *

from unittest import skip


from django.test import TestCase
from tabular_test_helper import TabularTest, INPUT_DIR

from shared_dataverse_information.tabular_import.forms import TabularUploadResultValidationForm


class TabularAPITester(TestCase):

    def setUp(self):
        pass
        #self.upload_california_census()
        #self.upload_mass_census()
        
    def tearDown(self):
        pass


    def add_shapefile_layer(self, title, shp_dirname, shp_fname_prefix):
        
        msgt('Upload Shapefile: %s' % title)
        tr = TabularTest()
        tr.login_for_cookie()

        # Upload Shapefile parts
        #shp_fname_prefix = 'tl_2014_25_tract'
        #shp_dirname = join(INPUT_DIR, shp_fname_prefix)
        result = tr.add_shapefile_layer(shp_dirname, shp_fname_prefix)
        msge(result)
        return result
        
        
    

    def upload_mass_census(self):

        msgt('Upload MA Census Shapefile')
        
        shp_fname_prefix = 'tl_2014_25_tract'
        
        return self.add_shapefile_layer('Massachusets Census'\
                            , join(INPUT_DIR, shp_fname_prefix)
                            , shp_fname_prefix\
                             )
                             
                             
    def upload_california_census(self):

         msgt('Upload CA Census Shapefile')

         shp_fname_prefix = 'tl_2013_06_tract'

         return self.add_shapefile_layer('California Census'\
                             , join(INPUT_DIR, shp_fname_prefix)\
                             , shp_fname_prefix\
                              )

    
    def test02_upload_and_join(self):
        
        msgt('test02_upload_and_join')
        
        #-----------------------------------------------
        msgn('Upload MA population tracts')
        #-----------------------------------------------
        tr = TabularTest()
        tr.login_for_cookie()        

        # --Upload and Join--
        join_props = {'title': 'CA Population', 'layer_typename': 'geonode:tl_2013_06_tract', 'table_attribute': 'geoid2', 'layer_attribute': 'GEOID'} 
        fname_to_upload = join(INPUT_DIR, 'ca_tracts_pop.csv')

        result = tr.upload_and_join(fname_to_upload, join_props)

        msg('result: %s' % result)
       
        """
        join_props = {'title': 'MA income'\
                        , 'layer_typename': 'geonode:tl_2014_25_tract_1'\
                        , 'layer_attribute': 'TRACTCE'\
                        , 'table_attribute': 'TRACT'\
                        }
        fname_to_upload = join(INPUT_DIR, 'boston_income.csv')

        result = tr.upload_and_join(fname_to_upload, join_props)

        msg('result: %s' % result)
        """
    
    @skip('skipping')
    def test01_good_tabular_join(self):
        
        msgt('test01_good_tabular_join')

        #-----------------------------------------------
        msgn('Upload CA population tracts')
        #-----------------------------------------------
        tr = TabularTest()
        tr.login_for_cookie()        

        # Upload CSV
        title = 'California population tracts'
        fname_to_upload = join(INPUT_DIR, 'ca_tracts_pop.csv')
        
        result = tr.upload_datatable_file(title, fname_to_upload)
        msg('result: %s' % result)
        
        f = TabularUploadResultValidationForm(result)
        if not f.is_valid():
            msg(f.errors)
        else:
            msg('looks good')
        
        
        #-----------------------------------------------
        msgn('Delete datatable')
        #-----------------------------------------------
        tr = TabularTest()
        tr.login_for_cookie()        
        #result = tr.delete_datatable(17)
        result = tr.delete_datatable(f.cleaned_data['datatable_id'])
        
        msg('result: %s' % result)
        



            
def upload_boston_income_csv():
    tr = TabularTest()
    tr.login_for_cookie()

    # Upload CSV
    title = 'Boston Income'
    fname_to_upload = join(INPUT_DIR, 'boston_income_73g.csv')
    
    #fname_to_upload = join(INPUT_DIR, 'boston_income_73g-1-row.csv')
    #fname_to_upload = join(INPUT_DIR, '2-ma-counties.csv')
    #fname_to_upload = join(INPUT_DIR, '2-ca-measures.csv')
    
    tr.upload_datatable_file(title, fname_to_upload)

    # boston_income_73g

def upload_boston_cenus_csv():
    tr = TabularTest()
    tr.login_for_cookie()

    # Upload CSV
    title = 'Boston Census'
    fname_to_upload = join(INPUT_DIR, 'c_bra_CSV-of-SHAPE.csv')
    tr.upload_datatable_file(title, fname_to_upload)




    # geonode:tl_2014_25_tract
def upload_ma_tigerlines_csv():
    tr = TabularTest()
    tr.login_for_cookie()

    # Upload CSV
    title = 'MA tigerlines Census'
    fname_to_upload = join(INPUT_DIR, 'tl_2014_25_tract.csv')
    tr.upload_datatable_file(title, fname_to_upload)
    
    #{"datatable_id": 34, "datatable_name": "tl_2014_25_tract"}

    
def join_boston_census():

    join_props = {
        'layer_typename' : 'geonode:c_bra_bl',  # underlying layer (orig shp)
        'layer_attribute': 'TRACT', # underlying layer - attribute
        'table_name': 'c_bra_csv_of_shape', # data table (orig csv)
        'table_attribute': 'TRACT', # data table - attribute
    }

    tr = TabularTest()
    tr.login_for_cookie()
    tr.join_datatable_to_layer(join_props)

def join_boston_income():
    # geonode:tl_2014_25_tract
     
    join_props = {
        'layer_typename' : 'geonode:tl_2014_25_tract',  # underlying layer (orig shp)
        'layer_attribute': 'TRACTCE', # underlying layer - attribute
        'table_name': 'boston_income_73g_lopalxy', # data table (orig csv)
        'table_attribute': 'tract', # data table - attribute
        #'table_name': 'boston_income_73g_1_row_yhahhul', # data table (orig csv)
    }
   
   
    tr = TabularTest()
    tr.login_for_cookie()
    tr.join_datatable_to_layer(join_props)
    
    
if __name__=='__main__':
    pass
    #-----------------------------
    # Join boston income to census
    #-----------------------------
    # (1) Add MA tigerlines: 
    # result: {"url": "/layers/geonode%3Atl_2014_25_tract", "success": true}
    #upload_ma_tigerlines()
    
    # (2) Add boston income csv
    #   result: {"datatable_id": 45, "datatable_name": "boston_income_73g_xdjkao3"}
    #upload_boston_income_csv()
    
    # (3) Try table join
    #join_boston_income()
    
    
