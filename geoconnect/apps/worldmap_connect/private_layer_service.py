from __future__ import print_function

from django.http import HttpResponse

import requests

from apps.worldmap_connect.models import WorldMapLayerInfo
#from apps.worldmap_connect.worldmap_api_url_helper import GET_VIEW_PRIVATE_LAYER_URL
from dataverse_info.forms_embed_layer import EmbedLayerForm
from dataverse_info.forms_api_validate import SIGNATURE_KEY
from dataverse_info.tests.msg_util import *
from django.conf import settings


"""
To display a private WorldMap layer
"""

"""
127.0.0.1:8070/shapefile/test-embed/
127.0.0.1:8000/dataverse-private-layer/view-private-layer/1e70f1ae8f9b43ff3e41870950e13e69c5ec14fab223930037a52cd6 
"""

def xget_private_worldmap_layer_link(worldmap_info):
    """
     {"message": "Success", "data": {"private_layer_url": "http://localhost:8000/dataverse-private-layer/view-private-layer/b3642470943c80e95866d222e0f587aa32d33d2f88bb8eca1a9a8f89"}, "success": true}

    :param worldmap_info:
    :return:
    """

    assert type(worldmap_info) is WorldMapLayerInfo, "worldmap_info must be a WorldMapLayerInfo object"

    """
    data = dict(dv_user_id=1\
                , datafile_id=86\
                , layer='transportation_to_work_v24_zip_mva'
                )
    """
    data = dict(layer=worldmap_info.layer_name\
                , dv_user_id=worldmap_info.import_attempt.gis_data_file.dv_user_id    # bit of stretch here
                , datafile_id=worldmap_info.import_attempt.gis_data_file.datafile_id \
                )

    f1 = EmbedLayerForm(data)
    params = None
    if f1.is_valid():
        #params = f1.clean_data
        params = f1.get_api_params_with_signature()

    print ('params', params)
    # POST option
    #url = 'http://localhost:8000/dataverse-private-layer/request-private-layer-url/'
    try:
        r = requests.post(GET_VIEW_PRIVATE_LAYER_URL, data=params)
    except:
        print ('ERROR!')
        return None


    if not r.status_code == 200:
        print ('ERROR!',  r.status_code)
        return None

    try:
        json_info = r.json()
        if json_info.has_key('data') and json_info['data'].has_key('private_layer_url'):
            private_layer_url = json_info['data']['private_layer_url']
            print ('private_layer_url', private_layer_url)
            return private_layer_url
    except:
        print ('text: %s' % r.text)
        print ('ERROR!',  r.status_code)
        return None

    print ('text: %s' % r.text)

    print ('ERROR!',  r.status_code)
    return None

 
    #return HttpResponse(r.text)
    page_text = """<html><head></head><body>
    <iframe id="id_iframe_map" height="275" width="100%" min-width="900" src="http://127.0.0.1:8000/dataverse-private-layer/view-private-layer/4402dcbd015eda52b9e8b1f451217c6fd175a11ad6d1097f228c604c" xsrc="http://localhost:8000/maps/embed/?layer=geonode:transportation_to_work_v24_zip_mva"></iframe>
    """
    page_text = """%s%s</body></html>""" % (page_text, r.text)
    
    return HttpResponse(page_text)
    
"""
python manage.py shell
from apps.worldmap_connect.models import WorldMapLayerInfo
from apps.worldmap_connect.private_layer_service import get_private_worldmap_layer_link

w = WorldMapLayerInfo.objects.all()[0]
w
get_private_worldmap_layer_link(w)
"""