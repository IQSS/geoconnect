from __future__ import print_function
import os, sys
import json
from os.path import basename, join, dirname, abspath, isfile

from osgeo import ogr, osr
import shapefile
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
    
def reproject_to_4326(shape_fname):
    
    if not isfile(shape_fname):
        msgx('File not found: %s' % shape_fname)
            
    driver = ogr.GetDriverByName('ESRI Shapefile')
    inDataSet = driver.Open(shape_fname)

    # input SpatialReference
    inLayer = inDataSet.GetLayer()
    inSpatialRef = inLayer.GetSpatialRef()
    
    # output SpatialReference
    outSpatialRef = osr.SpatialReference()
    outSpatialRef.ImportFromEPSG(4326)
    
    # create the CoordinateTransformation
    coordTrans = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)
    
    # create the output layer
    outputShapefile = get_output_fname(shape_fname, '_4326')
    #msg('output file: %s' % outputShapefile)
    
    if os.path.exists(outputShapefile):
        driver.DeleteDataSource(outputShapefile)
    outDataSet = driver.CreateDataSource(outputShapefile)
    outLayer = outDataSet.CreateLayer("basemap_4326", geom_type=ogr.wkbMultiPolygon)
    
    # add fields
    inLayerDefn = inLayer.GetLayerDefn()
    for i in range(0, inLayerDefn.GetFieldCount()):
        fieldDefn = inLayerDefn.GetFieldDefn(i)
        outLayer.CreateField(fieldDefn)
    
    # get the output layer's feature definition
    outLayerDefn = outLayer.GetLayerDefn()
    
    # loop through the input features
    inFeature = inLayer.GetNextFeature()
    while inFeature:
        # get the input geometry
        geom = inFeature.GetGeometryRef()
        # reproject the geometry
        geom.Transform(coordTrans)
        # create a new feature
        outFeature = ogr.Feature(outLayerDefn)
        # set the geometry and attribute
        outFeature.SetGeometry(geom)
        for i in range(0, outLayerDefn.GetFieldCount()):
            outFeature.SetField(outLayerDefn.GetFieldDefn(i).GetNameRef(), inFeature.GetField(i))
        # add the feature to the shapefile
        outLayer.CreateFeature(outFeature)
        # destroy the features and get the next input feature
        outFeature.Destroy()
        inFeature.Destroy()
        inFeature = inLayer.GetNextFeature()
    
    #msg(dir(outDataSet))
    #msg(outLayer.ExportToJson())
    
    # close the shapefiles
    inDataSet.Destroy()
    outDataSet.Destroy()
    
    
    msg('output file: %s' % outputShapefile)
    return outputShapefile
    
def convert_shp_to_geojson(shape_fname):
    if not isfile(shape_fname):
        msgx('File not found: %s' % shape_fname)
    
    try:
        # read the shapefile
        reader = shapefile.Reader(shape_fname)
    except:
        msgx('Failed to read shapefile: %s' % shape_fname)
        
    fields = reader.fields[1:]
    field_names = [field[0] for field in fields]
    output_buffer = []
    for sr in reader.shapeRecords():
          atr = dict(zip(field_names, sr.record))
          geom = sr.shape.__geo_interface__
          output_buffer.append(dict(type="Feature", geometry=geom, properties=atr))

    # write the GeoJSON file
    out_fname = os.path.join('page-out', basename(shape_fname).replace('.shp', '.json'))
   
    geojson = open(out_fname, "w")
    geojson.write(json.dumps({"type": "FeatureCollection","features": output_buffer}, indent=2) + "\n")
    geojson.close()    
    msg('file written: %s' % out_fname)

    return out_fname

def make_leaflet_page(geojson_file, ouput_html_fname):
    if not isfile(geojson_file):
        msgx('File not found: %s' % geojson_file)
    
    # Boston 
    mboston = folium.Map(location=[ 42.3267154, -71.1512353])
    mboston.geo_json(geojson_file)
    #mboston.geo_json('income.json')
    mboston.create_map(path=ouput_html_fname)
    print ('file written', ouput_html_fname)
    
if __name__=='__main__':
    reprojected_fname = reproject_to_4326('data/social_disorder_in_boston/social_disorder_in_boston_yqh.shp')
    
    geojson_fname = convert_shp_to_geojson(reprojected_fname)
    
    make_leaflet_page(geojson_fname, 'page-out/disorder.html')
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    