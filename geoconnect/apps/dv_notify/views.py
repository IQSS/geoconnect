from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse, Http404

from django.template import RequestContext
from django.core.urlresolvers import reverse
from apps.worldmap_connect.models import WorldMapLayerInfo
from apps.dv_notify.metadata_updater import MetadataUpdater
from geo_utils.message_helper_json import MessageHelperJSON


def view_ajax_notify_dv_of_map(request, worldmapinfo_md5):
    """
    Send WorldMapLayerInfo to Dataverse
    """

    # ------------------------------
    # Retrieve WorldMapLayerInfo
    # ------------------------------
    try:
        worldmap_layer_info = WorldMapLayerInfo.objects.get(md5=worldmapinfo_md5)
    except WorldMapLayerInfo.DoesNotExist:
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
from apps.dv_notify.metadata_updater import MetadataUpdater
from apps.gis_tabular.models import WorldMapJoinLayerInfo, WorldMapLatLngInfo

wm_info = WorldMapJoinLayerInfo.objects.get(pk=1)
#MetadataUpdater.update_dataverse_with_metadata(wm_info)

params = wm_info.get_params_for_dv_update()

api_update_url = 'https://dataverse.harvard.edu:443/api/worldmap/update-layer-metadata'
api_update_url = 'http://localhost:8080/api/worldmap/update-layer-metadata'

params['GEOCONNECT_TOKEN'] = '1d809464e26ba59byayayayy9752f631b829683f5c07692d'

r = requests.post(api_update_url, data=json.dumps(params))

params2 = {'mapLayerLinks': '{"json": "http://worldmap.harvard.edu/download/wfs/28033/json?outputFormat=json&service=WFS&request=GetFeature&format_options=charset%3AUTF-8&typename=geonode%3Anhcrime_201_ey&version=1.0.0", "csv": "http://worldmap.harvard.edu/download/wfs/28033/csv?outputFormat=csv&service=WFS&request=GetFeature&format_options=charset%3AUTF-8&typename=geonode%3Anhcrime_201_ey&version=1.0.0", "png": "http://worldmap.harvard.edu/download/wms/28033/png?layers=geonode%3Anhcrime_201_ey&width=736&bbox=-72.986767%2C41.252628%2C-72.859443%2C41.34771&service=WMS&format=image%2Fpng&srs=EPSG%3A4326&request=GetMap&height=550", "zip": "http://worldmap.harvard.edu/download/wfs/28033/zip?outputFormat=SHAPE-ZIP&service=WFS&request=GetFeature&format_options=charset%3AUTF-8&typename=geonode%3Anhcrime_201_ey&version=1.0.0", "gml": "http://worldmap.harvard.edu/download/wfs/28033/gml?outputFormat=text%2Fxml%3B+subtype%3Dgml%2F3.1.1&service=WFS&request=GetFeature&format_options=charset%3AUTF-8&typename=geonode%3Anhcrime_201_ey&version=1.0.0", "tiff": "http://worldmap.harvard.edu/download/wms/28033/tiff?layers=geonode%3Anhcrime_201_ey&width=736&bbox=-72.986767%2C41.252628%2C-72.859443%2C41.34771&service=WMS&format=image%2Fgeotiff&srs=EPSG%3A4326&request=GetMap&height=550", "KML": "http://worldmap.harvard.edu/download/wms_kml/28033/kml?layers=geonode%3Anhcrime_201_ey&mode=refresh", "xls": "http://worldmap.harvard.edu/download/wfs/28033/xls?outputFormat=excel&service=WFS&request=GetFeature&format_options=charset%3AUTF-8&typename=geonode%3Anhcrime_201_ey&version=1.0.0", "pdf": "http://worldmap.harvard.edu/download/wms/28033/pdf?layers=geonode%3Anhcrime_201_ey&width=736&bbox=-72.986767%2C41.252628%2C-72.859443%2C41.34771&service=WMS&format=application%2Fpdf&srs=EPSG%3A4326&request=GetMap&height=550", "jpg": "http://worldmap.harvard.edu/download/wms/28033/jpg?layers=geonode%3Anhcrime_201_ey&width=736&bbox=-72.986767%2C41.252628%2C-72.859443%2C41.34771&service=WMS&format=image%2Fjpeg&srs=EPSG%3A4326&request=GetMap&height=550"}', 'GEOCONNECT_TOKEN': u'0d0a7f65465d6bdbf0ac7b5d9d54aff7b9f3a80741624c45ec14b3fe1f611f03', 'joinDescription': '', 'embedMapLink': u'http://worldmap.harvard.edu/maps/embed/?layer=geonode:nhcrime_201_ey', 'mapImageLink': u'http://worldmap.harvard.edu/download/wms/28033/png?layers=geonode:nhcrime_201_ey&width=736&bbox=-72.9868,41.2526,-72.8594,41.3477&service=WMS&format=image/png&srs=EPSG:4326&request=GetMap&height=550', 'worldmapUsername': u'dataverse_user', 'layerName': u'nhcrime_201_ey', 'layerLink': u'http://worldmap.harvard.edu/data/geonode:nhcrime_201_ey', 'LatLngBoundingBox': u'[-72.986767, 41.252628, -72.859443, 41.34771]'}


for k, v in params.items(): print '\n', k, '\nv1:', v,'\nv2:', params2.get(k)

"""
