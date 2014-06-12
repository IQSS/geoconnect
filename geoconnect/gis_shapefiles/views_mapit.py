import os

import requests

from django.shortcuts import render
from django.shortcuts import render_to_response

from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

#from django.core.files.uploadedfile import SimpleUploadedFile


from gis_shapefiles.models import ShapefileSet, SingleFileInfo
from gis_shapefiles.shp_services import get_shapefile_from_dv_api_info

#from gis_shapefiles.views import view_choose_shapefile

import json
from django.http import Http404
#import urllib2
import logging
logger = logging.getLogger(__name__)

import urllib, cStringIO

# Create your views here.
# 
@login_required
def view_mapit_incoming(request, dv_session_token):
    """Quick view that needs major error checking
    
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

    # Attach timeout/error check here!
    r = requests.get(callback_url)
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

            choose_shapefile_url =  reverse('view_shapefile'\
                                            , kwargs={ 'shp_md5' : shp_md5 })
                                        
            return HttpResponseRedirect(choose_shapefile_url)
       

    """
    Add error page!!
    """
    return HttpResponse(str(jresp))
        
     
