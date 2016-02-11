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
