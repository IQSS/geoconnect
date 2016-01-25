from django.conf.urls import patterns, include, url


urlpatterns = patterns('apps.gis_tabular.views',

    url(r'^test1/(?P<tabular_id>\d{1,10})/$', 'view_test_file', name="view_test_file"),

    url(r'^ajax-join-targets/(?P<selected_geo_type>[\w|-]{1,255})/$', 'ajax_get_join_targets',\
        name='ajax_get_join_targets'),

    url(r'^ajax-join-targets-all/$', 'ajax_get_all_join_targets',\
        name='ajax_get_all_join_targets'),

    url(r'^check-lat-long-form/$', 'view_check_lat_lng_column_form',\
        name='view_check_lat_lng_column_form')
)
