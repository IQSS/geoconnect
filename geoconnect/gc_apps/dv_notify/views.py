"""
Convenience views for sending Layer metadata back to Dataverse via API
"""
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse, Http404

from django.template import RequestContext
from django.core.urlresolvers import reverse
from gc_apps.worldmap_connect.models import WorldMapLayerInfo
from gc_apps.dv_notify.metadata_updater import MetadataUpdater
from gc_apps.classification.utils import get_worldmap_info_object
from gc_apps.layer_types.static_vals import TYPE_SHAPEFILE_LAYER,\
                TYPE_JOIN_LAYER,\
                TYPE_LAT_LNG_LAYER
from geo_utils.message_helper_json import MessageHelperJSON


def ajax_dv_notify_shapefile_map(request, worldmapinfo_md5):
    """
    Retrieve a WorldMapLayerInfo object (from a shapefile) and send it to Dataverse
    """
    worldmap_layer_info = get_worldmap_info_object(TYPE_SHAPEFILE_LAYER, worldmapinfo_md5)
    if worldmap_layer_info is None:
        err_msg = 'WorldMapLayerInfo not found'
        json_msg = MessageHelperJSON.get_json_fail_msg(err_msg)
        return HttpResponse(json_msg, mimetype="application/json", status=404)

    return view_ajax_dv_notify_of_map(request, worldmap_layer_info)



def ajax_dv_notify_latlng_map(request, worldmapinfo_md5):
    """
    Retrieve a WorldMapJoinLayerInfo object and send it to Dataverse
    """
    worldmap_layer_info = get_worldmap_info_object(TYPE_LAT_LNG_LAYER, worldmapinfo_md5)
    if worldmap_layer_info is None:
        err_msg = 'WorldMapLatLngInfo not found'
        json_msg = MessageHelperJSON.get_json_fail_msg(err_msg)
        return HttpResponse(json_msg, mimetype="application/json", status=404)

    return view_ajax_dv_notify_of_map(request, worldmap_layer_info)


def ajax_dv_notify_tabular_join_map(request, worldmapinfo_md5):
    """
    Retrieve a WorldMapJoinLayerInfo object and send it to Dataverse
    """
    worldmap_layer_info = get_worldmap_info_object(TYPE_JOIN_LAYER, worldmapinfo_md5)
    if worldmap_layer_info is None:
        err_msg = 'WorldMapJoinLayerInfo not found'
        json_msg = MessageHelperJSON.get_json_fail_msg(err_msg)
        return HttpResponse(json_msg, mimetype="application/json", status=404)

    return view_ajax_dv_notify_of_map(request, worldmap_layer_info)


def view_ajax_dv_notify_of_map(request, worldmap_layer_info):
    """
    Given a WorldMap layer information, send it to Dataverse
    worldmap_info may be:
        - WorldMapJoinLayerInfo
        - WorldMapLatLngInfo
        - WorldMapLayerInfo
    """
    if worldmap_layer_info is None:
        err_msg = 'WorldMapLayerInfo not found'
        json_msg = MessageHelperJSON.get_json_fail_msg(err_msg)
        return HttpResponse(json_msg, mimetype="application/json", status=404)


    # ------------------------------
    # Send Dataverse Notification
    # ------------------------------
    success = MetadataUpdater.update_dataverse_with_metadata(worldmap_layer_info)
    if success:
        json_msg = MessageHelperJSON.get_json_success_msg('Data sent')
        return HttpResponse(json_msg, mimetype="application/json", status=200)
    else:
        json_msg = MessageHelperJSON.get_json_fail_msg('Failed to send data to dataverse')
        return HttpResponse(json_msg, mimetype="application/json", status=500)

"""
import requests, json
from gc_apps.dv_notify.metadata_updater import MetadataUpdater
from gc_apps.gis_tabular.models import WorldMapJoinLayerInfo, WorldMapLatLngInfo

wm_info = WorldMapLatLngInfo.objects.get(pk=1)
#MetadataUpdater.update_dataverse_with_metadata(wm_info)

params = wm_info.get_params_for_dv_update()

api_update_url = 'https://dataverse.harvard.edu:443/api/worldmap/update-layer-metadata'

req = requests.post(api_update_url, data=json.dumps(params))

params = {'mapLayerLinks': '{"json": "http://worldmap.harvard.edu/download/wfs/28033/json?outputFormat=json&service=WFS&request=GetFeature&format_options=charset%3AUTF-8&typename=geonode%3Anhcrime_201_ey&version=1.0.0", "csv": "http://worldmap.harvard.edu/download/wfs/28033/csv?outputFormat=csv&service=WFS&request=GetFeature&format_options=charset%3AUTF-8&typename=geonode%3Anhcrime_201_ey&version=1.0.0", "png": "http://worldmap.harvard.edu/download/wms/28033/png?layers=geonode%3Anhcrime_201_ey&width=736&bbox=-72.986767%2C41.252628%2C-72.859443%2C41.34771&service=WMS&format=image%2Fpng&srs=EPSG%3A4326&request=GetMap&height=550", "zip": "http://worldmap.harvard.edu/download/wfs/28033/zip?outputFormat=SHAPE-ZIP&service=WFS&request=GetFeature&format_options=charset%3AUTF-8&typename=geonode%3Anhcrime_201_ey&version=1.0.0", "gml": "http://worldmap.harvard.edu/download/wfs/28033/gml?outputFormat=text%2Fxml%3B+subtype%3Dgml%2F3.1.1&service=WFS&request=GetFeature&format_options=charset%3AUTF-8&typename=geonode%3Anhcrime_201_ey&version=1.0.0", "tiff": "http://worldmap.harvard.edu/download/wms/28033/tiff?layers=geonode%3Anhcrime_201_ey&width=736&bbox=-72.986767%2C41.252628%2C-72.859443%2C41.34771&service=WMS&format=image%2Fgeotiff&srs=EPSG%3A4326&request=GetMap&height=550", "KML": "http://worldmap.harvard.edu/download/wms_kml/28033/kml?layers=geonode%3Anhcrime_201_ey&mode=refresh", "xls": "http://worldmap.harvard.edu/download/wfs/28033/xls?outputFormat=excel&service=WFS&request=GetFeature&format_options=charset%3AUTF-8&typename=geonode%3Anhcrime_201_ey&version=1.0.0", "pdf": "http://worldmap.harvard.edu/download/wms/28033/pdf?layers=geonode%3Anhcrime_201_ey&width=736&bbox=-72.986767%2C41.252628%2C-72.859443%2C41.34771&service=WMS&format=application%2Fpdf&srs=EPSG%3A4326&request=GetMap&height=550", "jpg": "http://worldmap.harvard.edu/download/wms/28033/jpg?layers=geonode%3Anhcrime_201_ey&width=736&bbox=-72.986767%2C41.252628%2C-72.859443%2C41.34771&service=WMS&format=image%2Fjpeg&srs=EPSG%3A4326&request=GetMap&height=550"}', 'GEOCONNECT_TOKEN': u'0d0a7f65465d6bdbf0ac7b5d9d54aff7b9f3a80741624c45ec14b3fe1f611f03', 'joinDescription': None, 'embedMapLink': u'http://worldmap.harvard.edu/maps/embed/?layer=geonode:nhcrime_201_ey', 'mapImageLink': u'http://worldmap.harvard.edu/download/wms/28033/png?layers=geonode:nhcrime_201_ey&width=736&bbox=-72.9868,41.2526,-72.8594,41.3477&service=WMS&format=image/png&srs=EPSG:4326&request=GetMap&height=550', 'worldmapUsername': u'dataverse_user', 'layerName': u'nhcrime_201_ey', 'layerLink': u'http://worldmap.harvard.edu/data/geonode:nhcrime_201_ey', 'LatLngBoundingBox': u'[-72.986767, 41.252628, -72.859443, 41.34771]'}
"""
