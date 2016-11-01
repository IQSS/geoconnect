"""
Testing: Add a Map Layer Information to a Dataverse file by
calling the Dataverse API usually caleld by GeoConnect

Set up:
    - Upload a mappable file to your local Dataverse
    - Publish it
    - Click "Map Data"
    - Go to PgAdmin
        - Go to the "worldmapauth_token" table
    - Go to the latest entry and copy the "token" value
    - Past the value into the line below marked: "PUT YOUR GEOCONNECT_TOKEN HERE"
    - Run the script
"""
import requests
import json


payload =  {'mapLayerLinks': '{"json": "http://worldmap.harvard.edu/download/wfs/29145/json?outputFormat=json&service=WFS&request=GetFeature&format_options=charset%3AUTF-8&typename=geonode%3Aupdatedeva_g6x&version=1.0.0", "csv": "http://worldmap.harvard.edu/download/wfs/29145/csv?outputFormat=csv&service=WFS&request=GetFeature&format_options=charset%3AUTF-8&typename=geonode%3Aupdatedeva_g6x&version=1.0.0", "png": "http://worldmap.harvard.edu/download/wms/29145/png?layers=geonode%3Aupdatedeva_g6x&width=678&bbox=140.617908%2C37.2418281146%2C141.258962531%2C37.761795&service=WMS&format=image%2Fpng&srs=EPSG%3A4326&request=GetMap&height=550", "zip": "http://worldmap.harvard.edu/download/wfs/29145/zip?outputFormat=SHAPE-ZIP&service=WFS&request=GetFeature&format_options=charset%3AUTF-8&typename=geonode%3Aupdatedeva_g6x&version=1.0.0", "gml": "http://worldmap.harvard.edu/download/wfs/29145/gml?outputFormat=text%2Fxml%3B+subtype%3Dgml%2F3.1.1&service=WFS&request=GetFeature&format_options=charset%3AUTF-8&typename=geonode%3Aupdatedeva_g6x&version=1.0.0", "tiff": "http://worldmap.harvard.edu/download/wms/29145/tiff?layers=geonode%3Aupdatedeva_g6x&width=678&bbox=140.617908%2C37.2418281146%2C141.258962531%2C37.761795&service=WMS&format=image%2Fgeotiff&srs=EPSG%3A4326&request=GetMap&height=550", "KML": "http://worldmap.harvard.edu/download/wms_kml/29145/kml?layers=geonode%3Aupdatedeva_g6x&mode=refresh", "xls": "http://worldmap.harvard.edu/download/wfs/29145/xls?outputFormat=excel&service=WFS&request=GetFeature&format_options=charset%3AUTF-8&typename=geonode%3Aupdatedeva_g6x&version=1.0.0", "pdf": "http://worldmap.harvard.edu/download/wms/29145/pdf?layers=geonode%3Aupdatedeva_g6x&width=678&bbox=140.617908%2C37.2418281146%2C141.258962531%2C37.761795&service=WMS&format=application%2Fpdf&srs=EPSG%3A4326&request=GetMap&height=550", "jpg": "http://worldmap.harvard.edu/download/wms/29145/jpg?layers=geonode%3Aupdatedeva_g6x&width=678&bbox=140.617908%2C37.2418281146%2C141.258962531%2C37.761795&service=WMS&format=image%2Fjpeg&srs=EPSG%3A4326&request=GetMap&height=550"}',
'embedMapLink': u'https://worldmap.harvard.edu/maps/embed/?layer=geonode:updatedeva_g6x',
'GEOCONNECT_TOKEN': u'f2c56a6cdffbcf0sd4d0c4f60608e003d63313948cd5f31b0ec7319629182167c',
'joinDescription': None,
'mapImageLink': u'http://worldmap.harvard.edu/download/wms/6147/png?layers=geonode%3A_popcensuscomplete_4eo&width=832&bbox=118.13083807%2C19.6208224671%2C157.697678428%2C45.7735095957&service=WMS&format=image%2Fpng&srs=EPSG%3A4326&request=GetMap&height=550',
'worldmapUsername': u'dataverse_user',
'layerName': u'geonode:updatedeva_g6x',
'layerLink': u'http://worldmap.harvard.edu/maps/new/?layer=geonode:updatedeva_g6x',
'LatLngBoundingBox': u'[140.617908, 37.2418281145771, 141.258962531409, 37.761795]'}



#api_update_url = 'https://demo.dataverse.org:443/api/worldmap/update-layer-metadata'
api_update_url = 'http://localhost:8080/api/worldmap/update-layer-metadata'

print payload.keys()


payload['GEOCONNECT_TOKEN'] = 'PUT YOUR GEOCONNECT_TOKEN HERE'

req = requests.post(api_update_url,\
    data=json.dumps(payload))


print req.text
print req.status_code


#payload['mapLayerLinks'] = None
'''
required_params = """GEOCONNECT_TOKEN layerName layerLink worldmapUsername""".split()
payload2 = {}
for rq in required_params:
    payload2[rq] = payload[rq]
print payload2
'''
