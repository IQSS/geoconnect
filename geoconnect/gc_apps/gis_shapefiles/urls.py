from django.conf.urls import url
from gc_apps.gis_shapefiles.views_02_visualize import ViewAjaxVisualizeShapefile
from gc_apps.gis_shapefiles import views, views_mapit

urlpatterns = [

    url(r'^examine/$', views.view_examine_dataset, name="view_examine_dataset"),

    url(r'^view-shp-examine/(?P<shp_md5>\w{32})/$', views.view_shapefile_first_time, name="view_shapefile_first_time"),

    url(r'^view-shp/(?P<shp_md5>\w{32})/$', views.view_shapefile, name="view_shapefile"),

    url(r'^map-it/(?P<dataverse_token>\w{64})/$', views_mapit.view_mapit_incoming_token64, name="view_mapit_incoming_token64"),

    url(r'^ajax-visualize/(?P<shp_md5>\w{1,32})/$', ViewAjaxVisualizeShapefile.as_view(), name="view_ajax_attempt_visualization"),
]
