from django.conf.urls import patterns, include, url


urlpatterns = patterns('apps.worldmap_connect.views',

    url(r'^send-shapefile/(?P<shp_md5>\w{32})/$', 'view_send_shapefile_to_worldmap', name="view_send_shapefile_to_worldmap"),

    # for testing
    url(r'^send-metadata-to-dataverse/(?P<import_success_id>\d{1,10})/$', 'send_metadata_to_dataverse', name="send_metadata_to_dataverse"),

    url(r'^params-for-datavarse/(?P<import_success_id>\d{1,10})/$', 'show_import_success_params', name="show_import_success_params"),

)


