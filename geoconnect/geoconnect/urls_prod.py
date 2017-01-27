from django.conf import settings
from django.conf.urls.static import static

from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

URL_PREFIX = '' #'geo/'

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'gc_apps.content_pages.views.view_home', name="view_home"),

    url(r'^%sdv/' % URL_PREFIX, include('gc_apps.registered_dataverse.urls')),

    # url(r'^$', 'geoconnect.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^%sshapefile/' % URL_PREFIX, include('gc_apps.gis_shapefiles.urls')),

    url(r'^%stabular/' % URL_PREFIX, include('gc_apps.gis_tabular.urls')),

    #url(r'^%sgeoconnect/'% URL_PREFIX, include('gc_apps.gis_shapefiles.urls')),

    url(r'^%sworldmap/' % URL_PREFIX, include('gc_apps.worldmap_connect.urls')),

    url(r'^%sclassify/' % URL_PREFIX, include('gc_apps.classification.urls')),

    url(r'^%sdv-notify/' % URL_PREFIX, include('gc_apps.dv_notify.urls')),

    #url(r'^shp-view/', include('gis_shapefiles.urls')),

    #(r'^%s/geo-connect-admin/doc/' % URL_PREFIX, include('django.contrib.admindocs.urls')),

    url(r'^%sgeo-connect-admin/' % URL_PREFIX, include(admin.site.urls)),

)
