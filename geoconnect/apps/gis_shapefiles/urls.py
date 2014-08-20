from django.conf.urls import patterns, include, url


urlpatterns = patterns('apps.gis_shapefiles.views',
    url(r'^examine/$', 'view_examine_dataset', name="view_examine_dataset"),

    #url(r'^choose/(?P<shp_md5>\w{32})/$', 'view_choose_shapefile', name="view_choose_shapefile"),

    #url(r'^choose2/(?P<shp_md5>\w{32})/$', 'view_03_choose_shapefile_set', name="view_03_choose_shapefile_set"),

    url(r'^view-shp-initial/(?P<shp_md5>\w{32})/$', 'view_shapefile_first_time', name="view_shapefile_first_time"),

    url(r'^view-shp/(?P<shp_md5>\w{32})/$', 'view_shapefile', name="view_shapefile"),

    url(r'^delete-files/$', 'view_delete_files', name="view_delete_files"),
    url(r'^delete-worldmap-import-attempts/$', 'view_delete_worldmap_visualization_attempts', name="view_delete_worldmap_visualization_attempts"),

)

urlpatterns += patterns('apps.gis_shapefiles.views_mapit',
    #url(r'^map-it/(?P<dv_session_token>\w{32})/$', 'view_mapit_incoming', name="view_mapit_incoming"),

    #url(r'^map-it/(?P<dataset_id>\d{1,10})/$', 'view_mapit_incoming_no_token', name="view_mapit_incoming_no_token"),

    url(r'^map-it/(?P<dataverse_token>\w{64})/$', 'view_mapit_incoming_token64', name="view_mapit_incoming_token64"),
    
)

#urlpatterns += patterns('folium_maker.views',
#    url(r'^folium-test/(?P<shp_md5>\w{32})/$', 'view_try_folium', name="view_try_folium"),
#)



#urlpatterns += patterns('gis_shapefiles.views_field_check',
#    url(r'^shp/(?P<shp_md5>\w{32})/(?P<field_name>\w{1,200})/(?P<column_index>\d{1,7})/$', #'view_field_stats', name="view_field_stats"),
#)


"""
urlpatterns += patterns('gis_shapefiles.views_import',

    url(r'^examine-callback-url/$', 'view_shapefile_callback', name="view_shapefile_callback"),
    
)
"""
