from __future__ import print_function
import os, sys
from os.path import join, dirname, abspath
import json
import folium
import xlrd
import datetime

#from osgeo import ogr, osr
#import shapefile
import folium

def msg(s): print (s)
def dashes(): msg(40*'-')
def msgt(s): dashes(); msg(s); dashes()
def msgx(s): dashes(); msg('ERROR'); msg(s); dashes(); sys.exit(0)


def get_output_fname(fname, new_suffix):
    fparts = fname.split('.')
    if len(fparts[-1]) == 3:
        return '.'.join(fparts[:-1]) + new_suffix + '.' + fparts[-1]
    
    return fname + new_suffix

def add_excel_markers(fname, html_fname, lat_idx=13, lng_idx=12):
    if not os.path.isfile(fname):
        msgx('File not found: %s' % fname)
    
    xl_workbook = xlrd.open_workbook(fname)
    xl_sheet = xl_workbook.sheet_by_index(0)

    map_nh = folium.Map(location=[41.28, -72.88])
    
    num_cols = xl_sheet.ncols
    
    marker_cnt = 0
    for row_idx in range(0, xl_sheet.nrows):    # Iterate through rows
        #cell_obj = xl_sheet.cell(row_idx, col_idx)
        lat = xl_sheet.cell(row_idx, lat_idx).value
        lng = xl_sheet.cell(row_idx, lng_idx).value

        dt_val = xl_sheet.cell(row_idx, 0).value 
        dt_val = datetime.datetime(*xlrd.xldate_as_tuple(dt_val, xl_workbook.datemode))

        tm_val = xl_sheet.cell(row_idx, 1).value
        tm_val = xlrd.xldate_as_tuple(tm_val, xl_workbook.datemode)  
        time_value = datetime.time(*tm_val[3:])
        
        
        desc = xl_sheet.cell(row_idx, 3).value
        
        print (desc.__class__.__name__)
        d = """<b>Date</b>: %s<br /><b>Time</b>: %s<br /><b>Type</b>: %s""" % (dt_val.strftime('%m/%d/%Y'), time_value, str(desc))
        
        map_nh.simple_marker([lat, lng], popup=str(d))
        marker_cnt +=1
        if marker_cnt == 10: 
            break
    map_nh.create_map(path=html_fname)
    print ('file written: %s' % html_fname)
    os.system('open %s' %  html_fname)
    
if __name__=='__main__':
    excel_crime_data = join(dirname(dirname(abspath(__file__))), 'test_data', 'coded_data_2014_01.xls')
    add_excel_markers(excel_crime_data, 'nh_crime.html')
