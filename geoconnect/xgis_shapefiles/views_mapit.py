import os

from django.shortcuts import render
from django.shortcuts import render_to_response

from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.core.urlresolvers import reverse

#from django.core.files.uploadedfile import SimpleUploadedFile


from gis_shapefiles.forms import ShapefileGroupForm
from gis_shapefiles.models import ShapefileGroup, SingleShapefileSet, SingleFileInfo
from gis_shapefiles.shp_services import update_shapefileset_with_metadata, get_shapefile_group_md5_from_metadata

from gis_shapefiles.views import view_choose_shapefile

import json
from django.http import Http404
import urllib2
import logging
logger = logging.getLogger(__name__)

import urllib, cStringIO

# Create your views here.
def view_mapit_incoming(request, dv_token):
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
    
    callback_url = request.GET['cb'] + dv_token    
    request = urllib2.Request(callback_url)
    response = urllib2.urlopen(request)
    jresp = json.loads(response.read())
    if jresp.has_key('status') and jresp['status'] == 'success':
        shp_dict = {}
        shp_dict['name'] = jresp['dataset_name']
        shp_dict['dv_username'] = jresp['dv_username']
        shp_dict['dataset_link'] = jresp['dataset_file_location']
        shp_dict['filename'] = jresp['filename']
        
        shp_md5 = get_shapefile_group_md5_from_metadata(shp_dict)
        if shp_md5 is None:
            raise Exception('shp_md5 failure: %s' % shp_dict)

        choose_shapefile_url =  reverse('view_choose_shapefile'\
                                            , kwargs={ 'shp_md5' : shp_md5 })
                                        
        return HttpResponseRedirect(choose_shapefile_url)
        """
        file_url = jresp['dataset_file_location']
        f = urllib.urlopen(file_url)
        
        post_dict = {'name': jresp['dataset_name'], 'dv_username' : jresp['dv_username']}
        file_dict = {'shp_file': SimpleUploadedFile(jresp['filename'], f.read())}
        shp_form = ShapefileGroupForm(post_dict, file_dict)
        if not shp_form.is_valid():
            return HttpResponse(shp_form.errors)xw
        
        shape_file_helper_obj = shp_form.save()
        """
        #return HttpResponse(shape_file_helper_obj.md5)
        #return view_choose_shapefile(request, shape_file_helper_obj.md5  )
        return HttpResponseRedirect(reverse('view_choose_shapefile'\
                                        , kwargs={ 'shp_md5' : shape_group_obj.md5 })\
                                    )
    return HttpResponse(str(jresp))
        
     

    img_temp = NamedTemporaryFile(delete=True)
    img_temp.write(urllib2.urlopen(url).read())
    img_temp.flush()

    im.file.save(img_filename, File(img_temp))