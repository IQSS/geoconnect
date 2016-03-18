from __future__ import print_function
import logging

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from geo_utils.msg_util import *

from apps.classification.layer_link_helper import LayerLinkHelper

LOGGER = logging.getLogger(__name__)

@login_required
def view_show_lawyer_links(request):

    if not 'layer' in request.GET:
        d = dict(error_message='Please specify a "?layer=" in the url')
        return render_to_response('classification/view_show_lawyer_links.html'\
                            , d
                            , context_instance=RequestContext(request))


    layer_name = request.GET.get('layer', None)
    if layer_name is None or len(layer_name.strip()) == 0:
        d = dict(error_message='Please specify a "?layer=" name in the url')
        return render_to_response('classification/view_show_lawyer_links.html'\
                            , d
                            , context_instance=RequestContext(request))


    link_helper = LayerLinkHelper(layer_name)

    d = dict(link_helper=link_helper)

    return render_to_response('classification/view_show_lawyer_links.html'\
                            , d
                            , context_instance=RequestContext(request))
