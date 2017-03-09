from django.conf import settings
from django.conf.urls.static import static

from django.conf.urls import include, url
from gc_apps.content_pages import views

from django.contrib import admin
admin.autodiscover()

URL_PREFIX = '' #'geo/'

urlpatterns = [

    url(r'^$', views.view_home, name="view_home"),

    url(r'^%sdv/' % URL_PREFIX, include('gc_apps.registered_dataverse.urls')),

    url(r'^%sshapefile/' % URL_PREFIX, include('gc_apps.gis_shapefiles.urls')),

    url(r'^%stabular/' % URL_PREFIX, include('gc_apps.gis_tabular.urls')),

    url(r'^%sworldmap/' % URL_PREFIX, include('gc_apps.worldmap_connect.urls')),

    url(r'^%sclassify/' % URL_PREFIX, include('gc_apps.classification.urls')),

    url(r'^%sdv-notify/' % URL_PREFIX, include('gc_apps.dv_notify.urls')),

    url(r'^%sgeo-connect-admin/' % URL_PREFIX, include(admin.site.urls)),

]


if settings.DEBUG:
    # Serve media files form the dev server
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Show the debug toolbar
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]

admin.site.site_header = 'Geoconnect (Dataverse <--> WorldMap)'
