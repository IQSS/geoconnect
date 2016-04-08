from django.conf.urls import patterns, include, url

urlpatterns = patterns('apps.dv_notify.views',

   url(r'^shapefile-map/(?P<worldmapinfo_md5>\w{1,32})/$', 'ajax_dv_notify_shapefile_map', name="ajax_dv_notify_shapefile_map"),

   url(r'^tabular-join-map/(?P<worldmapinfo_md5>\w{1,32})/$', 'ajax_dv_notify_tabular_join_map', name="ajax_dv_notify_tabular_join_map"),

   url(r'^latlng-map/(?P<worldmapinfo_md5>\w{1,32})/$', 'ajax_dv_notify_latlng_map', name="ajax_dv_notify_latlng_map"),
)
