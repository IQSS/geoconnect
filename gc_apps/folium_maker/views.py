from django.shortcuts import render
from gc_apps.gis_shapefiles.models import ShapefileInfo

from folium_maker.folium_converter import FoliumConverter
from django.contrib.auth.decorators import login_required

from django.shortcuts import render

from django.http import HttpResponseRedirect, HttpResponse, Http404

# Create your views here.
@login_required
def view_try_folium(request, shp_md5):
    d = {}
    try:
        shapefile_info = ShapefileInfo.objects.get(md5=shp_md5)
        d['shapefile_info'] = shapefile_info
        
    except ShapefileInfo.DoesNotExist:
        logger.error('Shapefile not found for hash: %s' % shp_md5)
        raise Http404('Shapefile not found.')
        
    fc = FoliumConverter(shapefile_info, request)
    
    # Another super-hack for test
    
    return HttpResponseRedirect(fc.folium_map.folium_url)
    