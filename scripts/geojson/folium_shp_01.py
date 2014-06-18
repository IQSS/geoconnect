from __future__ import print_function
import os, sys
import json

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
    """From the Python GDAL/OGR Cookbook
    
    Source: http://pcjericks.github.io/py-gdalogr-cookbook/projection.html#reproject-a-layer
    
    :param shape_fname: full file path to a shapefile (.shp)
    :returns: full file path to a shapefile reprojected as 4326
    """
    if not os.path.isfile(shape_fname):
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
        
    # close the shapefiles
    inDataSet.Destroy()
    outDataSet.Destroy()
    
    
    msg('output file: %s' % outputShapefile)
    return outputShapefile
    
def convert_shp_to_geojson(shape_fname):
    """Using the pyshp library, https://github.com/GeospatialPython/pyshp, convert the shapefile to JSON
    
    Code is from this example:  http://geospatialpython.com/2013/07/shapefile-to-geojson.html
    
    :param shape_fname: full file path to a shapefile (.shp)
    :returns: full file path to a GEOJSON representation of the shapefile
    
    (recheck/redo using gdal)
    """
    if not os.path.isfile(shape_fname):
        msgx('File not found: %s' % shape_fname)
    
    # Read the shapefile
    try: 
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
    out_fname = os.path.join('page-out', os.path.basename(shape_fname).replace('.shp', '.json'))
   
    geojson = open(out_fname, "w")
    geojson.write(json.dumps({"type": "FeatureCollection","features": output_buffer}, indent=2) + "\n")
    geojson.close()    
    msg('file written: %s' % out_fname)

    return out_fname
    

def make_leaflet_page(geojson_files=[], ouput_html_fname='leaflet_page.html'):
    """Using folium, make an HTML page using GEOJSON input 
        examples: https://github.com/wrobstory/folium
            
    :param geojson_file: full file path to a GEO JSON file
    :param ouput_html_fname: name of HTML file to create (will only use the basename)
    """
    if not type(geojson_files) in [dict, list]:
        msgx('geojson_files should be a list or tupe, not a %s' % geojson_files.__class__.__name__)
        
    for geojson_file in geojson_files:
        if not os.path.isfile(geojson_file):
            msgx('File not found: %s' % geojson_file)
    
    # Boston 
    mboston = folium.Map(location=[ 42.3267154, -71.1512353])
    for geojson_file in geojson_files:
        mboston.geo_json(geojson_file)
    
    #mboston.geo_json('income.json')
    ouput_html_fname = os.path.basename(ouput_html_fname)
    mboston.create_map(path=ouput_html_fname)
    print ('file written', ouput_html_fname)
    
    
if __name__=='__main__':
    reprojected_fname = reproject_to_4326('data/social_disorder_in_boston/social_disorder_in_boston_yqh.shp')
    geojson_fname = convert_shp_to_geojson(reprojected_fname)
    make_leaflet_page([geojson_fname], 'disorder.html')
    #make_leaflet_page([geojson_fname, 'data/HOSPITALS.geojson'], 'disorder.html')
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    