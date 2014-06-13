from django.shortcuts import render
from django.shortcuts import render_to_response

from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from gis_shapefiles.models import ShapefileSet, SingleFileInfo
#from gis_shapefiles.views import view_choose_shapefile

from django.conf import settings  
import os
import logging
logger = logging.getLogger(__name__)

import shapefile

from numpy.random import randn
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np

def to_percent(y, position):
    # Ignore the passed in position. This has the effect of scaling the default
    # tick locations.
    s = str(100 * y)

    # The percent symbol needs escaping in latex
    if matplotlib.rcParams['text.usetex'] == True:
        return s + r'$\%$'
    else:
        return s + '%'

def get_data_array(shapefile_set, col_idx):
    if shapefile_set is None:
        return None
    if col_idx is None or not col_idx.isdigit():
        return None

    shp_info = shapefile_set.get_shp_fileinfo_obj()
    if shp_info is None:
        return None
        
    sf = shapefile.Reader(shp_info.extracted_file_path)  # basename
    data = [rec[int(col_idx)] for rec in sf.records()]
    #print sf.records()
    return data

def count_unique(keys):
    uniq_keys = np.unique(keys)
    bins = uniq_keys.searchsorted(keys)
    return uniq_keys, np.bincount(bins)
    
# Create your views here.
@login_required
def view_field_stats(request, shp_md5, field_name, column_index):
    """
    In progress.  Examine the contents of a given field for a shapefile.

    **Context** 
    
    ``RequestContext``

    :field_name: str, name of the column to examine
    :shp_md5: 32-char str, unique md5 hash for a :model:`gis_shapefiles.ShapefileSet`
    :column_index: int, index of the column to examine
    
    
    **Template:**

    :template:`gis_shapefiles/view_04_field_info.html`
    """
    d = { 'page_title' : 'Column Information: %s' % field_name}
    try:
        shp_set = ShapefileSet.objects.get(md5=shp_md5)
    except ShapefileSet.DoesNotExist:
        raise Http404('ShapefileSet not found for: %s' % shp_md5)
    
    d['page_title'] = '%s: %s' % (shp_set.get_basename(), field_name)
    
    data_array = get_data_array(shp_set, column_index)
    
    plt.barh(range(len(data_array)), data_array)
    
    img_name_for_web = os.path.join('plots', '%s-%s.png' % (shp_md5, column_index))
    img_name_fullpath = os.path.join(settings.MEDIA_ROOT, img_name_for_web)
    
    """
    pyplot.hist(data_array, bins=5, facecolor='green', alpha=0.75)
    pyplot.xlabel('Time (ms)')
    pyplot.ylabel('Count')
    pyplot.suptitle(r'Sup title')
    pyplot.title(r'Title')
    """
    
    #pyplot.grid(True)
    plt.savefig(img_name_fullpath)
        
    d['plot_url'] = img_name_for_web
    d['shapefile_set'] = shp_set
    d['field_name'] = field_name
    d['data_array'] = data_array
    #pylab.savefig('foo.png')
    return render_to_response('view_04_field_info.html', d\
                                     , context_instance=RequestContext(request))
                                     
    return HttpResponse('%s %s %s<br />%s<br />%s' % (shp_md5, field_name, column_index, data_array, img_name_fullpath))
    
