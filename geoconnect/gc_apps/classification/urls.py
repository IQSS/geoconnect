from django.conf.urls import patterns, include, url


urlpatterns = patterns('gc_apps.classification.views',
    #url(r'^classify-layer/(?P<shapefile_md5>\w{32})/(?P<import_success_md5>\w{32})$', 'view_classify_layer_form', name="view_classify_layer_form"),
    url(r'^classify-layer/(?P<import_success_md5>\w{32})$', 'view_classify_layer_form', name="view_classify_layer_form"),

)

urlpatterns += patterns('gc_apps.classification.views_debug',
    #url(r'^classify-layer/(?P<shapefile_md5>\w{32})/(?P<import_success_md5>\w{32})$', 'view_classify_layer_form', name="view_classify_layer_form"),
    url(r'^show-layer-links/?$', 'view_show_lawyer_links', name="view_show_lawyer_links"),

)
