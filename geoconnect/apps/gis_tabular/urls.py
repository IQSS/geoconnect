from django.conf.urls import patterns, include, url


urlpatterns = patterns('apps.gis_tabular.views',

    url(r'^test1/(?P<tabular_id>\d{1,10})/$', 'view_test_1', name="view_test_1"),

)


