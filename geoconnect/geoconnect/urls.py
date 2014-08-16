from django.conf import settings
from django.conf.urls.static import static

from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

URL_PREFIX = 'geo/'

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'geoconnect.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^%sshapefile/' % URL_PREFIX, include('gis_shapefiles.urls')),

    url(r'^%sgeoconnect/'% URL_PREFIX, include('gis_shapefiles.urls')),

    url(r'^%sworldmap/' % URL_PREFIX, include('worldmap_import.urls')),

    url(r'^%sclassify/' % URL_PREFIX, include('classification.urls')),

    #url(r'^shp-view/', include('gis_shapefiles.urls')),

    #(r'^%s/geo-connect-admin/doc/' % URL_PREFIX, include('django.contrib.admindocs.urls')),
    
    url(r'^%sgeo-connect-admin/' % URL_PREFIX, include(admin.site.urls)),
    
) 
#+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Uncomment the next line to serve media files in dev.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
                            url(r'^__debug__/', include(debug_toolbar.urls)),
                            )
