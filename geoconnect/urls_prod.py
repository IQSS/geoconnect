
from django.conf.urls import url, include
from gc_apps.content_pages import views
from django.contrib import admin
admin.autodiscover()

URL_PREFIX = '' #'geo/'

urlpatterns = [
    # Examples:
    url(r'^$', views.view_home, name="view_home"),

    url(r'^%sdv/' % URL_PREFIX, include('gc_apps.registered_dataverse.urls')),

    url(r'^%sshapefile/' % URL_PREFIX, include('gc_apps.gis_shapefiles.urls')),

    url(r'^%stabular/' % URL_PREFIX, include('gc_apps.gis_tabular.urls')),

    url(r'^%sworldmap/' % URL_PREFIX, include('gc_apps.worldmap_connect.urls')),

    url(r'^%sclassify/' % URL_PREFIX, include('gc_apps.classification.urls')),

    url(r'^%sdv-notify/' % URL_PREFIX, include('gc_apps.dv_notify.urls')),

    # Admin
    url(r'^%sgeo-connect-admin/' % URL_PREFIX, include(admin.site.urls)),

]

admin.site.site_header = 'Geoconnect (Dataverse <--> WorldMap)'
