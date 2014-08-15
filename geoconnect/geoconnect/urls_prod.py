from django.conf import settings
from django.conf.urls.static import static

from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

URL_PREFIX = 'geo'

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'geoconnect.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^%s/shapefile/' % URL_PREFIX, include('gis_shapefiles.urls')),

    url(r'^%s/geoconnect/'% URL_PREFIX, include('gis_shapefiles.urls')),

    url(r'^%s/worldmap/' % URL_PREFIX, include('worldmap_import.urls')),

    url(r'^%s/classify/' % URL_PREFIX, include('classification.urls')),

    #url(r'^shp-view/', include('gis_shapefiles.urls')),

    #(r'^%s/geo-connect-admin/doc/' % URL_PREFIX, include('django.contrib.admindocs.urls')),
    
    url(r'^%s/geo-connect-admin/' % URL_PREFIX, include(admin.site.urls)),
    
) 
