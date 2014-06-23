import os
import json

from django.shortcuts import render_to_response

from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.core.urlresolvers import reverse

from geo_utils.json_field_reader import MessageHelperJSON

from gis_shapefiles.models import ShapefileSet
from worldmap_import.models import WorldMapImportAttempt, WorldMapImportFail, WorldMapImportSuccess
from worldmap_import.worldmap_importer import WorldMapImporter
from dv_notify.metadata_updater import MetadataUpdater


import logging
logger = logging.getLogger(__name__)

try:
    from test_token import WORLDMAP_TOKEN_FOR_DV, WORLDMAP_SERVER_URL
except:
    WORLDMAP_TOKEN_FOR_DV = 'fake-key'
    WORLDMAP_SERVER_URL = 'http://worldmap-fake-url.harvard.edu'


def show_import_success_params(request, import_success_id):

    try:
        wm_success = WorldMapImportSuccess.objects.get(pk=import_success_id)
    except WorldMapImportSuccess.DoesNotExist:
        return HttpResponse('WorldMapImportSuccess object not found: %s' % import_success_id)

    return HttpResponse('%s' % wm_success.get_data_dict())


def send_metadata_to_dataverse(request, import_success_id):
    try:
        wm_success = WorldMapImportSuccess.objects.get(pk=import_success_id)
    except WorldMapImportSuccess.DoesNotExist:
        return HttpResponse('WorldMapImportSuccess object not found: %s' % import_success_id)
    
    MetadataUpdater.update_dataverse_with_metadata(wm_success)
    if wm_success.import_attempt.gis_data_file:
        lnk = reverse('view_shapefile'\
                    , kwargs={ 'shp_md5' : wm_success.import_attempt.gis_data_file.md5 }\
                    )
        return HttpResponseRedirect(lnk)
    return HttpResponse('metadata sent')
    
def view_send_shapefile_to_worldmap(request, shp_md5):
    """
    *** This will be async via celery ***
    Send a shapefile over to WorldMap for import and record the results.
    A successful import should return a new layer name as well as links to this layer
    
    :param shp_md5: md5 of a ShapefileSet object
    :type shp_md5: str
    :returns: JSON with "success" flag and either error or data
    :rtype: JSON string
    
    Example of successful import by WorldMap: 
     { "success": true, "data": {"layer_link": "http://localhost:8000/data/geonode:poverty_1990_gfz_zip_p5n", "worldmap_username": "saru_jaya", "layer_name": "geonode:poverty_1990_gfz_zip_p5n", "embed_map_link": "http://localhost:8000/maps/embed/?layer=geonode:poverty_1990_gfz_zip_p5n"}}
    """

    # (1) Retrieve the ShapefileSet object
    print '(1) Retrieve the ShapefileSet object'
    try:
        shapefile_set = ShapefileSet.objects.get(md5=shp_md5)
    except ShapefileSet.DoesNotExist:
        data = MessageHelperJSON.get_json_mesg(False, 'Sorry, the shapefile was not found')
        return HttpResponse(data, mimetype='application/json')
    
    print '(2) Check if it has a valid shapefile (or that shapefile has been validated)'
    
    # (2) Check if it has a valid shapefile (or that shapefile has been validated)
    if not shapefile_set.has_shapefile:
        data = MessageHelperJSON.get_json_mesg(False, 'This file does not contain a valid shapefile')
        return HttpResponse(data, mimetype='application/json')

    print '(3a) Look for a previous import attempt (WorldMapImportAttempt) object related to this ShapefileSet'
    # (3a) Look for a previous import attempt (WorldMapImportAttempt) object related to this ShapefileSet
    #
    wm_attempt = WorldMapImportAttempt.get_latest_attempt(shapefile_set)
    if wm_attempt and wm_attempt.did_import_succeed():

        print '(3b) If the previous attempt succeeded, return the results'
        # (3b) If the previous attempt succeeded, return the results
        success_info = wm_attempt.get_success_info()
        print 'success_info', success_info
        if success_info:
            #data = MessageHelperJSON.get_json_mesg(True\
            #                    , 'Success: %s<br /> %s' % (success_info, success_info.layer_name))
            # hack before ajax is hooked up
            return HttpResponseRedirect(reverse('view_shapefile'\
                                        , kwargs={ 'shp_md5' : shp_md5 })\
                                    )
            return HttpResponse(success_info.get_as_json_message(), mimetype='application/json')
    
    print '(4) Create a new WorldMapImportAttempt'
    # (4) Create a new WorldMapImportAttempt
    #
    if wm_attempt is None:
        zipped_shapefile_name = os.path.basename(shapefile_set.dv_file.name)
        wm_attempt = WorldMapImportAttempt(gis_data_file=shapefile_set\
                                    , title=zipped_shapefile_name\
                                    , abstract='[place holder abstract for %s]' % shapefile_set.name\
                                    , shapefile_name=zipped_shapefile_name\
                                    )
        wm_attempt.save()
    
    print '(5) Prepare parameters (title, abstract, etc) to send with the import request'
    # (5) Prepare parameters (title, abstract, etc) to send with the import request
    #
    layer_params = wm_attempt.get_params_for_worldmap_import(geoconnect_token=WORLDMAP_TOKEN_FOR_DV)

    print '(6) Instantiate the WorldMapImporter object and attempt the import'
    # (6) Instantiate the WorldMapImporter object and attempt the import
    # *** This part of the process will be moved to a celery queue -- asyn b/c it may take a while ***
    #
    wmi = WorldMapImporter(WORLDMAP_SERVER_URL)
    worldmap_response = wmi.send_shapefile_to_worldmap(layer_params, shapefile_set.dv_file.path)
    
    print '-' *40
    print worldmap_response
    print '-' *40
    
    print '(7) Check if import worked.  '
    # (7) Check if import worked.  
    #
    #
    import_success = worldmap_response.get('success', False)

    if import_success is True:  # Import appears to have worked
        
        wm_data = worldmap_response.get('data', None)
        if wm_data is None:
            # Failed, where is the data?  Create a WorldMapImportFail object
            #
            wm_fail = WorldMapImportFail(import_attempt=wm_attempt\
                                            , msg="Error.  WorldMap says success but no layer data found"\
                                            , orig_response='%s' % worldmap_response)
            wm_fail.save()
        else:       
            wm_success = None 
            try:
                # Success!  Create a WorldMapImportSuccess object
                #
                wm_success = WorldMapImportSuccess(import_attempt=wm_attempt\
                                                , layer_name=wm_data.get('layer_name', '')\
                                                , layer_link=wm_data.get('layer_link', '')\
                                                , embed_map_link=wm_data.get('embed_map_link', '')\
                                                , worldmap_username=wm_data.get('worldmap_username', '')\
                                            )
                wm_success.save()
                wm_attempt.import_success = True
                wm_attempt.save()
            except:
                # Fail! Something in the return data seems to be incorrect.  e.g., Missing parameter such as layer_link
                # Save a WorldMapImportFail object to check original response
                #
                wm_fail = WorldMapImportFail(import_attempt=wm_attempt\
                                                , msg="Error.  WorldMap says success.  geoconnect failed to save results"\
                                                , orig_response='%s' % worldmap_response)
                wm_fail.save()
            
            try:
                # Separate this into another async. task!
                # Send message back to the Dataverse -- to update metadata
                #
                # Round-trip example, break into separate process with 
                #   MetadataUpdateFail, MetadataUpdateSuccess objects
                #
                MetadataUpdater.update_dataverse_with_metadata(wm_success)
            except:
                wm_fail = WorldMapImportFail(import_attempt=wm_attempt\
                                                , msg="Error.  Layer created and saved BUT update to dataverse failed."\
                                                , orig_response='%s' % worldmap_response)
                wm_fail.save()
            
            
            #if wm_success:
            #    return HttpResponse(wm_success.get_as_json_message(), mimetype='application/json')
            
                
                # hack before ajax is hooked up
                #return HttpResponseRedirect(reverse('view_shapefile'\
                #                            , kwargs={ 'shp_md5' : shp_md5 })\
                #                        )
                   
            
                                            
    else:
        # Fail! Save a WorldMapImportFail object to check original response
        #
        msg = worldmap_response.get('message', 'Import Failed')
        wm_fail = WorldMapImportFail(import_attempt=wm_attempt\
                                    , msg=msg)
        wm_fail.save()
    
    
    
    return HttpResponseRedirect(reverse('view_shapefile', kwargs={'shp_md5': shp_md5 }))
    
    json_msg = json.dumps(worldmap_response)
    return HttpResponse(json_msg, mimetype='application/json')
    
    #print( wmi.send_shapefile_to_worldmap2('St Louis income 1990', 'St. Louis data', f1, 'raman_prasad@harvard.edu'))
    
    