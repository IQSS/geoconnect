"""
Quick hit: no err checking (yet)
"""
from __future__ import print_function
import os, sys
import json
import shutil
import zipfile
from osgeo import ogr, osr
import shapefile
import folium

if __name__=='__main__':
    CURRENT_DIR = os.path.dirname(os.path.dirname(__file__))

    sys.path.append(os.path.join(CURRENT_DIR, '../'))
    sys.path.append(os.path.join(CURRENT_DIR, '../../'))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geoconnect.settings")



from folium_maker.models import FoliumMap
from django.conf import settings

def msg(s): print (s)
def dashes(): msg(40*'-')
def msgt(s): dashes(); msg(s); dashes()
def msgx(s): dashes(); msg('ERROR'); msg(s); dashes(); sys.exit(0)

class FoliumConverter:
    
    def __init__(self, gis_data_file):
        self.err_found = False
        self.err_msg = None
        self.folium_map = None
        self.gis_data_file = gis_data_file
        self.make_map()
    
    def make_map(self):
        if not self.gis_data_file.dv_file:
            self.err_found = True
            self.err_msg = 'There is not GIS file to convert'
        
        self.folium_map = FoliumMap(name=os.path.basename(self.gis_data_file.dv_file.name)\
                            , gis_data_file=self.gis_data_file\
                            )
        self.folium_map.save()
        
        output_dir = self.folium_map.get_output_directory()
        
        # (1) Copy DV file to folium output directory
        copied_gis_fname = os.path.join(output_dir, self.folium_map.name )
        
        orig_file_fullpath = os.path.join(settings.MEDIA_ROOT, self.gis_data_file.dv_file.name)
        shutil.copy(orig_file_fullpath, copied_gis_fname)
        msg('file copied: %s' % copied_gis_fname)
        
        # (2) Extract file
        fh = open(copied_gis_fname, 'rb')
        z = zipfile.ZipFile(fh)
        shp_fname = None
        for name in z.namelist():
            if name.startswith('_'): continue
            outpath = os.path.dirname(copied_gis_fname)
            z.extract(name, outpath)
            if name.endswith('.shp'):
                shp_fname = os.path.join(outpath, name)
            print(name, outpath)
        fh.close()
        
        if shp_fname is None:
            self.err_found = True
            self.err_msg = 'No shapefile found in .zip'
            
        #with zipfile.ZipFile(copied_gis_fname, "r") as z:
        #    z.extractall(os.path.dirname(copied_gis_fname))
        #    msg(z.name) 
        #return
        
        # Reproject copied dv file
        #shp_fname = os.path.splitext(self.folium_map.name)[0]
        reprojected_fname = reproject_to_4326(shp_fname)
        geojson_fname, center_lat, center_lng = convert_shp_to_geojson(reprojected_fname, output_dir)

        html_page_name = os.path.splitext(self.folium_map.name)[0] + '.html'
        
        kwargs = { 'center_lat': center_lat, 'center_lng': center_lng}
        make_leaflet_page([geojson_fname], output_dir, html_page_name, **kwargs)

        full_folium_path = os.path.join(output_dir, html_page_name)
        
        path_parts = full_folium_path.split('/media')
        #/Users/rmp553/Documents/iqss-git/geoconnect/test_setup', 'http://127.0.0.1:8000

        self.folium_map.folium_url = 'http://127.0.0.1:8000/media' + path_parts[1]
        self.folium_map.save()

        #make_leaflet_page([geojson_fname, 'data/HOSPITALS.geojson'], 'disorder.html')

        
        
        #     folium_url = models.URLField(blank=True)
        ##       zip_checker = ShapefileZipCheck(os.path.join(settings.MEDIA_ROOT, shapefile_set.dv_file.name))
                
                
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
    msgt('reproject_to_4326: %s' % shape_fname)
    if not os.path.isfile(shape_fname):
        msgx('File not found: %s' % shape_fname)
            
    #
    outputShapefile = get_output_fname(shape_fname, '_4326')
    
    #cmd = '''ogr2ogr -f "ESRI Shapefile" %s %s''' % (outputShapefile, shape_fname)# output.shp input.gml
    #cmd = '''ogr2ogr -f "ESRI Shapefile" %s %s -s_srs EPSG:27700 -t_srs EPSG:4326''' % (outputShapefile, shape_fname)
    cmd = '''ogr2ogr -f "ESRI Shapefile" %s %s -t_srs EPSG:4326''' % (outputShapefile, shape_fname)
    os.system(cmd)

    return outputShapefile
    
    #
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
    
def convert_shp_to_geojson(shape_fname, output_dir='page-out'):
    """Using the pyshp library, https://github.com/GeospatialPython/pyshp, convert the shapefile to JSON
    
    Code is from this example:  http://geospatialpython.com/2013/07/shapefile-to-geojson.html
    
    :param shape_fname: full file path to a shapefile (.shp)
    :returns: full file path to a GEOJSON representation of the shapefile
    
    (recheck/redo using gdal)
    """
    msgt('convert_shp_to_geojson: %s' % shape_fname)
    if not os.path.isfile(shape_fname):
        msgx('File not found: %s' % shape_fname)
    
    # Read the shapefile
    try: 
        reader = shapefile.Reader(shape_fname)
    except:
        msgx('Failed to read shapefile: %s' % shape_fname)
    
    lat_min, lng_min, lat_max, lng_max = reader.bbox
    print(lat_min, lng_min, lat_max, lng_max )
    center_lat = (lat_min+lat_max) / 2
    center_lng = (lng_min+lng_max) / 2
    
    fields = reader.fields[1:]
    field_names = [field[0] for field in fields]
    output_buffer = []
    for sr in reader.shapeRecords():
          atr = dict(zip(field_names, sr.record))
          geom = sr.shape.__geo_interface__
          output_buffer.append(dict(type="Feature", geometry=geom, properties=atr))

    # write the GeoJSON file
    out_fname = os.path.join(output_dir, os.path.basename(shape_fname).replace('.shp', '.json'))
   
    geojson = open(out_fname, "w")
    geojson.write(json.dumps({"type": "FeatureCollection","features": output_buffer}, indent=2) + "\n")
    geojson.close()    
    msg('file written: %s' % out_fname)

    return (out_fname, center_lat, center_lng)
    

def make_leaflet_page(geojson_files=[], output_dir='.', output_html_fname='leaflet_page.html', **kwargs):
    """Using folium, make an HTML page using GEOJSON input 
        examples: https://github.com/wrobstory/folium
            
    :param geojson_file: full file path to a GEO JSON file
    :param output_html_fname: name of HTML file to create (will only use the basename)
    """
    if not type(geojson_files) in [dict, list]:
        msgx('geojson_files should be a list or tupe, not a %s' % geojson_files.__class__.__name__)
        
    for geojson_file in geojson_files:
        if not os.path.isfile(geojson_file):
            msgx('File not found: %s' % geojson_file)
    
    # Boston 
    center_lat = kwargs.get('center_lat', 42.3267154)
    center_lng = kwargs.get('center_lng', -71.1512353)
    mboston = folium.Map(location=[center_lng, center_lat ])
    for geojson_file in geojson_files:
        mboston.geo_json(geojson_file)
    
    #mboston.geo_json('income.json')
    output_html_fname = os.path.basename(output_html_fname)
    mboston.create_map(path=os.path.join(output_dir, output_html_fname))
    
    print ('file written', output_html_fname)
    html_fullpath = os.path.join(output_dir, output_html_fname)
    
    # Real hack to make path work through server
    fh = open(html_fullpath, 'r'); content = fh.read(); fh.close()
    content = content.replace('/Users/rmp553/Documents/iqss-git/geoconnect/test_setup', 'http://127.0.0.1:8000')
    fh = open(html_fullpath, 'w'); fh.write(content); fh.close()
    
    
if __name__=='__main__':
    from gis_shapefiles.models import ShapefileSet
    l = ShapefileSet.objects.filter(id=0)
    if l.count() == 0:
        msgx('no files in database')
    s = l[0]
    msg(s)
    fc = FoliumConverter(s)
    """
    reprojected_fname = reproject_to_4326('data/social_disorder_in_boston/social_disorder_in_boston_yqh.shp')
    geojson_fname, center_lat, center_lng = convert_shp_to_geojson(reprojected_fname)
    make_leaflet_page([geojson_fname], 'disorder.html')
    #make_leaflet_page([geojson_fname, 'data/HOSPITALS.geojson'], 'disorder.html')
    """
    
    
    
    
    
    