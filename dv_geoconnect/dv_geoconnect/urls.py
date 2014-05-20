from django.conf import settings
from django.conf.urls.static import static

from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'dv_geoconnect.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^shapefile/', include('gis_shapefiles.urls')),

    url(r'^geoconnect/', include('gis_shapefiles.urls')),

    #url(r'^shp-view/', include('gis_shapefiles.urls')),

    url(r'^geo-connect-admin/', include(admin.site.urls)),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
