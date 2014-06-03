from django.conf.urls import patterns, include, url


urlpatterns = patterns('worldmap_import.views',

    url(r'^send-shapefile/(?P<shp_md5>\w{32})/$', 'view_send_shapefile_to_worldmap', name="view_send_shapefile_to_worldmap"),

    # for testing
    url(r'^send-metadata-to-dataverse/(?P<import_success_id>\d{1,10})/$', 'send_metadata_to_dataverse', name="send_metadata_to_dataverse"),

)


