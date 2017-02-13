"""Views for sending information to the Dataverse"""
from django.conf.urls import url
from gc_apps.dv_notify import views

urlpatterns = [\
   url(r'^shapefile-map/(?P<worldmapinfo_md5>\w{1,32})/$', views.ajax_dv_notify_shapefile_map,
       name="ajax_dv_notify_shapefile_map"),

   url(r'^tabular-join-map/(?P<worldmapinfo_md5>\w{1,32})/$', views.ajax_dv_notify_tabular_join_map,
       name="ajax_dv_notify_tabular_join_map"),

   url(r'^latlng-map/(?P<worldmapinfo_md5>\w{1,32})/$', views.ajax_dv_notify_latlng_map,
       name="ajax_dv_notify_latlng_map")]
