from __future__ import print_function

from django.http import HttpResponse

import requests

from dataverse_info.forms_embed_layer import EmbedLayerForm
from dataverse_info.forms_api_validate import SIGNATURE_KEY
from dataverse_info.tests.msg_util import *
from django.conf import settings

"""
127.0.0.1:8070/shapefile/test-embed/
127.0.0.1:8000/dataverse-private-layer/view-private-layer/10e585652204ef3c60c1e289f157c3480cb8e7704bc2bf78903f71e8
"""

def view_test_embed(request):
    data = dict(dv_user_id=1\
                , datafile_id=86\
                , layer='transportation_to_work_v24_zip_mva'
                )
    f1 = EmbedLayerForm(data)
    params = None
    if f1.is_valid():
        #params = f1.clean_data
        params = f1.get_api_params_with_signature()

    print ('params', params)
    # POST option
    url = 'http://localhost:8000/dataverse-private-layer/request-private-layer-url/'
    r = requests.post(url, data=params)

    print ('status: %s' % r.status_code)
    print ('text: %s' % r.text)
    #print ('json: %s' % r.json())
  
    #return HttpResponse(r.text)
    page_text = """<html><head></head><body>
    <iframe id="id_iframe_map" height="275" width="100%" min-width="900" src="http://127.0.0.1:8000/dataverse-private-layer/view-private-layer/4402dcbd015eda52b9e8b1f451217c6fd175a11ad6d1097f228c604c" xsrc="http://localhost:8000/maps/embed/?layer=geonode:transportation_to_work_v24_zip_mva"></iframe>
    """
    page_text = """%s%s</body></html>""" % (page_text, r.text)
    
    return HttpResponse(page_text)
    
    