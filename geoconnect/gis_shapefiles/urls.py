from django.conf.urls import patterns, include, url


urlpatterns = patterns('gis_shapefiles.views',
    url(r'^examine/$', 'view_examine_dataset', name="view_examine_dataset"),

    #url(r'^choose/(?P<shp_md5>\w{32})/$', 'view_choose_shapefile', name="view_choose_shapefile"),

    #url(r'^choose2/(?P<shp_md5>\w{32})/$', 'view_03_choose_shapefile_set', name="view_03_choose_shapefile_set"),

    url(r'^view-shp/(?P<shp_md5>\w{32})/$', 'view_shapefile', name="view_shapefile"),
)

urlpatterns += patterns('gis_shapefiles.views_mapit',
    url(r'^shp/(?P<dv_token>\w{56})/$', 'view_mapit_incoming', name="view_mapit_incoming"),

)


urlpatterns += patterns('gis_shapefiles.views_field_check',
    url(r'^shp/(?P<shp_md5>\w{32})/(?P<field_name>\w{1,200})/(?P<column_index>\d{1,7})/$', 'view_field_stats', name="view_field_stats"),

)


"""
urlpatterns += patterns('gis_shapefiles.views_import',

    url(r'^examine-callback-url/$', 'view_shapefile_callback', name="view_shapefile_callback"),
    
)
"""
