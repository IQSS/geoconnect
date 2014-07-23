from django.shortcuts import render
from gis_shapefiles.models import ShapefileSet

from folium_maker.folium_converter import FoliumConverter
from django.contrib.auth.decorators import login_required

from django.shortcuts import render_to_response

from django.http import HttpResponseRedirect, HttpResponse, Http404

# Create your views here.
@login_required
def view_try_folium(request, shp_md5):
    d = {}
    try:
        shapefile_set = ShapefileSet.objects.get(md5=shp_md5)
        d['shapefile_set'] = shapefile_set        
        
    except ShapefileSet.DoesNotExist:
        logger.error('Shapefile not found for hash: %s' % shp_md5)
        raise Http404('Shapefile not found.')
        
    fc = FoliumConverter(shapefile_set, request)
    
    # Another super-hack for test
    
    return HttpResponseRedirect(fc.folium_map.folium_url)
    