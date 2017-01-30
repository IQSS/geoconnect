from django.conf.urls import url
from gc_apps.worldmap_connect import views

urlpatterns = [

    url(r'^send-shapefile/(?P<shp_md5>\w{32})/$', views.view_send_shapefile_to_worldmap, name="view_send_shapefile_to_worldmap"),

    # for testing
    url(r'^send-metadata-to-dataverse/(?P<import_success_id>\d{1,10})/$', views.send_metadata_to_dataverse, name="send_metadata_to_dataverse"),

    url(r'^params-for-datavarse/(?P<import_success_id>\d{1,10})/$', views.show_import_success_params, name="show_import_success_params"),

    url(r'^clear-jointarget-info/$', views.clear_jointarget_info, name="clear_jointarget_info"),
    
]
