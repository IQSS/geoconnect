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

from apps.gis_shapefiles.models import ShapefileSet, SingleFileInfo
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
        raise Http404('no callback')
    
    if not request.GET.has_key('cb'):
        raise Http404('no callback url')
        
    callback_url = request.GET['cb']# + "?%s" % urlencode(dict(key='pete'))    
    
    TOKEN_PARAM = { settings.DATAVERSE_TOKEN_KEYNAME : dataverse_token }
    r = requests.post(callback_url, data=json.dumps(TOKEN_PARAM))
    msgt(r.text)
    msg(r.status_code)
    if not r.status_code == 200:
        return HttpResponse("Sorry! Failed to retrieve Dataverse file")

    jresp = r.json()
    if not type(jresp) is dict:
        return HttpResponse("Sorry! Failed to convert response to JSON")
    
    if jresp.has_key('status') and jresp['status'] in ['OK', 'success']:
        shp_md5 = get_shapefile_from_dv_api_info(dataverse_token, jresp.get('data'))
    
        if shp_md5 is None:
            raise Exception('shp_md5 failure: %s' % shp_md5)

        choose_shapefile_url =  reverse('view_shapefile_first_time'\
                                        , kwargs={ 'shp_md5' : shp_md5 })
                                    
        return HttpResponseRedirect(choose_shapefile_url)
        return HttpResponse("Good so far")
    
    return HttpResponse("Good so far")
    


#@login_required
'''
def view_mapit_incoming(request, dv_session_token):
    """For miniverse testing
    
    Quick view that needs major error checking
    
    (1) receive token + callback url
    (2) try url to retrieve metadata
    (3) use metadata to retrieve the file
    (4) create Shapefile Group object
    """
    # expects  ?token=
    if not request.GET:
        raise Http404('no token')
    
    if not request.GET.has_key('cb'):
        raise Http404('no callback url')
    
    callback_url = request.GET['cb'] + dv_session_token    
    msgt('callback_url: %s' % callback_url)
    # Attach timeout/error check here!
    r = requests.get(callback_url)
    msg("resp: %s" % r.text)
    msg("status: %s" % r.status_code)
    jresp = r.json()
    #return HttpResponse(dv_token)
    
    print jresp
    #return HttpResponse(jresp)
    
    if jresp.has_key('status') and jresp['status'] == 'success':
        if jresp.has_key('data'):
            print '-' * 40
            print jresp.get('data')
            print '-' * 40
            shp_md5 = get_shapefile_from_dv_api_info(dv_session_token, jresp.get('data'))
        
            if shp_md5 is None:
                raise Exception('shp_md5 failure: %s' % shp_md5)

            choose_shapefile_url =  reverse('view_shapefile_first_time'\
                                            , kwargs={ 'shp_md5' : shp_md5 })
                                        
            return HttpResponseRedirect(choose_shapefile_url)
       

    """
    Add error page!!
    """
    return HttpResponse(str(jresp))
'''        

     