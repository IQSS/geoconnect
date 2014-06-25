# Parse a delimited text file of volcano data and create a shapefile
import osgeo.ogr as ogr
import osgeo.osr as osr

from os.path import join, dirname, abspath, isfile
from collections import Counter
import xlrd
from xlrd.sheet import ctype_text   


# use a dictionary reader so we can access by field name
#reader = csv.DictReader(open("volcano_data.txt","rb"),
#    delimiter='\t',
#    quoting=csv.QUOTE_NONE)

fname = '../test_data/tabular/meth_labs-01.xls'
wb = xlrd.open_workbook(fname)
xl_sheet = wb.sheet_by_index(0)
col_names = xl_sheet.row(0)

# set up the shapefile driver
driver = ogr.GetDriverByName("ESRI Shapefile")

# create the data source
data_source = driver.CreateDataSource("meth_labs.shp")

# create the spatial reference, WGS84
srs = osr.SpatialReference()
srs.ImportFromEPSG(4326)

# create the layer
layer = data_source.CreateLayer("meth_labs", srs, ogr.wkbPoint)

# Add the fields we're interested in
#field_date = ogr.FieldDefn("Date", ogr.OFTDate )
#field_date.SetWidth(24)
#layer.CreateField(field_date)

#field_region = ogr.FieldDefn("Region", ogr.OFTString)
#field_region.SetWidth(24)
#layer.CreateField(field_region)
layer.CreateField(ogr.FieldDefn("Date"), ogr.OFTDate)
layer.CreateField(ogr.FieldDefn("Latitude"), ogr.OFTReal)
layer.CreateField(ogr.FieldDefn("Longitude"), ogr.OFTReal)
#layer.CreateField(ogr.FieldDefn("Elevation", ogr.OFTInteger))


# Process the text file and add the attributes and features to the shapefile
for row_idx in range(1, xl_sheet.nrows):
    # create the feature
    feature = ogr.Feature(layer.GetLayerDefn())
    
    feature.SetField("Date", xl_sheet.cell(row_idx, 0).value)
    
    lat_val = xl_sheet.cell(row_idx, 3).value
    lng_val = xl_sheet.cell(row_idx, 4).value
    #print lat_val.value, lng_val.value.__class__.__name__
    feature.SetField("Latitude", lat_val)
    feature.SetField("Longitude", lng_val)
    #cell_obj = 
            
    # Set the attributes using the values from the delimited text file
    #feature.SetField("Name", row['Name'])
    #feature.SetField("Region", row['Region'])
    #feature.SetField("Latitude", row['Latitude'])
    #feature.SetField("Longitude", row['Longitude'])
    #feature.SetField("Elevation", row['Elev'])

    # create the WKT for the feature using Python string formatting
    wkt = "POINT(%f %f)" %  (lng_val, lat_val)

    # Create the point from the Well Known Txt
    point = ogr.CreateGeometryFromWkt(wkt)

    # Set the feature geometry using the point
    feature.SetGeometry(point)
    # Create the feature in the layer (shapefile)
    layer.CreateFeature(feature)
    # Destroy the feature to free resources
    feature.Destroy()

# Destroy the data source to free resources
data_source.Destroy()
