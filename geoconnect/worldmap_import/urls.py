from django.conf.urls import patterns, include, url


urlpatterns = patterns('worldmap_import.views',

    url(r'^send-shapefile/(?P<shp_md5>\w{32})/$', 'view_send_shapefile_to_worldmap', name="view_send_shapefile_to_worldmap"),
)


