from django.conf.urls import patterns, include, url


urlpatterns = patterns('apps.gis_tabular.views',

    url(r'^test1/(?P<tabular_id>\d{1,10})/$', 'view_test_file', name="view_test_file"),

    url(r'^test2-sample-map/$', 'view_sample_map', name="view_sample_map"),

    url(r'^ajax-join-targets/(?P<selected_geo_type>[\w|-]{1,255})/$', 'ajax_get_join_targets',\
        name='ajax_get_join_targets'),

    url(r'^ajax-join-targets-all/$', 'ajax_get_all_join_targets',\
        name='ajax_get_all_join_targets'),

    url(r'^process-lat-long-form/$', 'view_process_lat_lng_column_form',\
        name='view_process_lat_lng_column_form'),

    url(r'^process-tabular-form/$', 'view_map_tabular_file_form',\
        name='view_map_tabular_file_form')

)
