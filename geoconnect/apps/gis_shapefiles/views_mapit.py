import os

import requests

from django.shortcuts import render
from django.shortcuts import render_to_response

from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.conf import settings

#from django.core.files.uploadedfile import SimpleUploadedFile
from geo_utils.msg_util import *

from apps.gis_shapefiles.models import ShapefileInfo, SingleFileInfo
from apps.gis_shapefiles.shp_services import get_shapefile_from_dv_api_info

#from apps.gis_shapefiles.views import view_choose_shapefile

from urllib import urlencode
import json
from django.http import Http404
#import urllib2
import logging
logger = logging.getLogger(__name__)

import urllib, cStringIO


def view_mapit_incoming_token64(request, dataverse_token):
    if not request.GET:
        logger.error('view_mapit_incoming_token64: no get params')
        raise Http404('no callback')
    
    if not request.GET.has_key('cb'):
        logger.error('view_mapit_incoming_token64: no callback parameter')
        raise Http404('no callback url')
        
    callback_url = request.GET['cb']# + "?%s" % urlencode(dict(key='pete'))    
    
    TOKEN_PARAM = { settings.DATAVERSE_TOKEN_KEYNAME : dataverse_token }
    r = requests.post(callback_url, data=json.dumps(TOKEN_PARAM))
    msgt(r.text)
    msg(r.status_code)
    if not r.status_code == 200:
        logger.error('view_mapit_incoming_token64. status code: %s\nresponse: %s' % (r.status_code, r.text))
        return HttpResponse("Sorry! Failed to retrieve Dataverse file")

    jresp = r.json()
    if not type(jresp) is dict:
        logger.error('view_mapit_incoming_token64. Failed to convert response to JSON\nstatus code: %s\nresponse: %s' % (r.status_code, r.text))        
        return HttpResponse("Sorry! Failed to convert response to JSON")
    
    if jresp.has_key('status') and jresp['status'] in ['OK', 'success']:
        data_dict = jresp.get('data')

        # ------------------------------------
        # FIX - when common dataverse_info object is in
        # ------------------------------------

        shp_md5 = get_shapefile_from_dv_api_info(dataverse_token, data_dict)#jresp.get('data'))
    
        if shp_md5 is None:
            raise Exception('shp_md5 failure: %s' % shp_md5)

        choose_shapefile_url =  reverse('view_shapefile_first_time'\
                                        , kwargs={ 'shp_md5' : shp_md5 })
                                    
        return HttpResponseRedirect(choose_shapefile_url)
        #return HttpResponse("Good so far")
    
    return HttpResponse("Good so far")
    


