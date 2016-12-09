from django.conf.urls import patterns, include, url
from apps.gis_shapefiles.views_02_visualize import ViewAjaxVisualizeShapefile

urlpatterns = patterns('apps.gis_shapefiles.views',
    url(r'^examine/$', 'view_examine_dataset', name="view_examine_dataset"),

    #url(r'^choose/(?P<shp_md5>\w{32})/$', 'view_choose_shapefile', name="view_choose_shapefile"),

    #url(r'^choose2/(?P<shp_md5>\w{32})/$', 'view_03_choose_shapefile_set', name="view_03_choose_shapefile_set"),

    url(r'^view-shp-examine/(?P<shp_md5>\w{32})/$', 'view_shapefile_first_time', name="view_shapefile_first_time"),

    #url(r'^view-shp-visualize/(?P<shp_md5>\w{32})/$', 'view_shapefile_visualize_attempt', #name="view_shapefile_visualize_attempt"),

    url(r'^view-shp/(?P<shp_md5>\w{32})/$', 'view_shapefile', name="view_shapefile"),

)

urlpatterns += patterns('apps.gis_shapefiles.views_mapit',
    #url(r'^map-it/(?P<dv_session_token>\w{32})/$', 'view_mapit_incoming', name="view_mapit_incoming"),

    #url(r'^map-it/(?P<dataset_id>\d{1,10})/$', 'view_mapit_incoming_no_token', name="view_mapit_incoming_no_token"),

    url(r'^map-it/(?P<dataverse_token>\w{64})/$', 'view_mapit_incoming_token64', name="view_mapit_incoming_token64"),

)


urlpatterns += patterns('apps.gis_shapefiles.views_02_visualize',

   url(r'^ajax-visualize/(?P<shp_md5>\w{1,32})/$', ViewAjaxVisualizeShapefile.as_view(), name="view_ajax_attempt_visualization"),
)

#urlpatterns += patterns('apps.gis_shapefiles.view_quick_test',
#    url(r'^test-embed/?$', 'view_test_embed', name="view_test_embed"),
#)

#urlpatterns += patterns('folium_maker.views',
#    url(r'^folium-test/(?P<shp_md5>\w{32})/$', 'view_try_folium', name="view_try_folium"),
#)
