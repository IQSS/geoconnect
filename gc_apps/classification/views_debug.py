from __future__ import print_function
import logging

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from gc_apps.classification.layer_link_helper import LayerLinkHelper

LOGGER = logging.getLogger(__name__)

@login_required
def view_show_lawyer_links(request):

    if not 'layer' in request.GET:
        d = dict(error_message='Please specify a "?layer=" in the url')
        return render(request,
                            'classification/view_show_lawyer_links.html'\
                            , d)


    layer_name = request.GET.get('layer', None)
    if layer_name is None or len(layer_name.strip()) == 0:
        d = dict(error_message='Please specify a "?layer=" name in the url')
        return render(request,
                        'classification/view_show_lawyer_links.html',
                        d)


    link_helper = LayerLinkHelper(layer_name)

    d = dict(link_helper=link_helper)

    return render(request,
                 'classification/view_show_lawyer_links.html',
                 d)
