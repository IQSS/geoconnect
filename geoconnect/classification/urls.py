from django.conf.urls import patterns, include, url


urlpatterns = patterns('classification.views',
    url(r'^classify-layer/(?P<shapefile_md5>\w{32})/(?P<import_success_md5>\w{32})$', 'view_classify_layer_form', name="view_classify_layer_form"),

)
