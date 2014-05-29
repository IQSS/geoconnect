import os
import json

from django.shortcuts import render_to_response

from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.core.urlresolvers import reverse

from geo_utils.json_field_reader import get_json_str_msg

from gis_shapefiles.models import ShapefileSet
from worldmap_import.models import WorldMapImportAttempt, WorldMapImportFail, WorldMapImportSuccess
from worldmap_import.worldmap_importer import WorldMapImporter



import logging
logger = logging.getLogger(__name__)

try:
    from test_token import WORLDMAP_TOKEN_FOR_DV, WORLDMAP_SERVER_URL
except:
    WORLDMAP_TOKEN_FOR_DV = 'fake-key'
    WORLDMAP_SERVER_URL = 'http://worldmap-fake-url.harvard.edu'

def view_send_shapefile_to_worldmap(request, shp_md5):
    d = {}

    try:
        shapefile_set = ShapefileSet.objects.get(md5=shp_md5)
        d['shapefile_set'] = shapefile_set        
    except ShapefileSet.DoesNotExist:
        
        logger.error('Shapefile not found for hash: %s' % shp_md5)
        raise Http404('Shapefile not found.')
        
    if not shapefile_set.has_shapefile:
        data = json.dumps(get_json_str_msg(False, 'This file does not contain a valid shapefile'))
        return HttpResponse(data, mimetype='application/json')

    # send_shapefile_to_worldmap(self, layer_params, fullpath_to_file)
    zipped_shapefile_name = os.path.basename(shapefile_set.dv_file.name)
    
    # Look for previous attempt before doing this!
    wm_attempt = WorldMapImportAttempt(gis_data_file=shapefile_set\
                                    , title=zipped_shapefile_name\
                                    , abstract='[place holder abstract for %s]' % shapefile_set.name\
                                    , shapefile_name=zipped_shapefile_name\
                                    )
    wm_attempt.save()
    
    layer_params = wm_attempt.get_params_for_worldmap_import(geoconnect_token=WORLDMAP_TOKEN_FOR_DV)
    wmi = WorldMapImporter(WORLDMAP_SERVER_URL)
    print layer_params
    data = wmi.send_shapefile_to_worldmap(layer_params, shapefile_set.dv_file.path)
    print 'data'
    print '-' *40
    print data
    
    """{'data': {u'layer_link': u'http://localhost:8000/data/geonode:poverty_1990_gfz_zip_p5n', u'worldmap_username': u'raman_prasad', u'layer_name': u'geonode:poverty_1990_gfz_zip_p5n', u'success': True, u'embed_map_link': u'http://localhost:8000/maps/embed/?layer=geonode:poverty_1990_gfz_zip_p5n'}, 'success': True}"""
    
    import_worked = data.get('success', False)
    if import_worked:
        wm_data = data.get('data', None)
        if wm_data is None:
            wm_fail = WorldMapImportFail(import_attempt=wm_attempt\
                                            , msg="Error.  WorldMap says success not no layer data found")
            wm_fail.save()
        else:        
            try:
                #wm_data.update({ 'import_attempt' : wm_attempt})            
                wm_success = WorldMapImportSuccess(import_attempt=wm_attempt\
                                                , layer_name=wm_data.get('layer_name', '')\
                                                , layer_link=wm_data.get('layer_link', '')\
                                                , embed_map_link=wm_data.get('embed_map_link', '')\
                                                , worldmap_username=wm_data.get('worldmap_username', '')\
                                            )
                wm_success.save()
            except:
                wm_fail = WorldMapImportFail(import_attempt=wm_attempt\
                                                , msg="Error.  WorldMap says success.  geoconnect failed to save results")
                wm_fail.save()
                        
                                            
    else:
        msg = data.get('message', 'Import Failed')
        wm_fail = WorldMapImportFail(import_attempt=wm_attempt\
                                    , msg=msg)
        wm_fail.save()
        
    
    json_msg = json.dumps(data)
    return HttpResponse(json_msg, mimetype='application/json')
    
    #print( wmi.send_shapefile_to_worldmap2('St Louis income 1990', 'St. Louis data', f1, 'raman_prasad@harvard.edu'))
    
    