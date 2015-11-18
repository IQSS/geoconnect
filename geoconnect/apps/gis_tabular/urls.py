from django.conf.urls import patterns, include, url


urlpatterns = patterns('apps.gis_tabular.views',

    url(r'^test1/(?P<tabular_id>\d{1,10})/$', 'view_test_1', name="view_test_1"),

    url(r'^ajax-join-targets/(?P<selected_geo_type>[\w|-]{1,255})/$', 'ajax_get_join_targets',\
        name='ajax_get_join_targets'),

    url(r'^ajax-join-targets-all/$', 'ajax_get_all_join_targets',\
        name='ajax_get_all_join_targets'),
)
