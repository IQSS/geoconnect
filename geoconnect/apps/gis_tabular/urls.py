from django.conf.urls import patterns, include, url


urlpatterns = patterns('apps.gis_tabular.views',

    url(r'^test/latest/$', 'view_tabular_file_latest', name="view_tabular_file_latest"),

    #url(r'^test1/(?P<tabular_id>\d{1,10})/$', 'view_tabular_file', name="view_tabular_file"),

    url(r'^view-tab-examine/(?P<tab_md5>\w{32})/$', 'view_tabular_file', name="view_tabular_file"),

    url(r'^view-existing-map/$', 'view_existing_map', name="view_existing_map"),

    # Join targets returned in list of tuples (id, name)
    #
    url(r'^ajax-join-targets/(?P<selected_geo_type>[\w|-]{1,255})/$', 'ajax_get_join_targets',\
        name='ajax_get_join_targets'),

    url(r'^ajax-join-targets/$', 'ajax_get_all_join_targets',\
        name='ajax_get_all_join_targets'),

    # Join targets returned in JSON format with id, name, and description
    #
    url(r'^ajax-join-targets-with-descriptions/$', 'ajax_get_all_join_targets_with_descriptions',\
        name='ajax_get_all_join_targets_with_descriptions'),

    url(r'^ajax-join-targets-with-descriptions/(?P<selected_geo_type>[\w|-]{1,255})/$', 'ajax_join_targets_with_descriptions',\
        name='ajax_join_targets_with_descriptions'),

    url(r'^view-unmatched-join-rows/(?P<tab_md5>\w{32})/$', 'view_unmatched_join_rows',\
        name='view_unmatched_join_rows'),

    url(r'^view-unmatched-lat-lng-rows/(?P<tab_md5>\w{32})/$', 'view_unmatched_lat_lng_rows',\
        name='view_unmatched_lat_lng_rows'),


)

urlpatterns += patterns('apps.gis_tabular.views_create_layer',

    url(r'^process-lat-long-form/$', 'view_process_lat_lng_form',\
        name='view_process_lat_lng_form'),

    url(r'^process-tabular-form/$', 'view_map_tabular_file_form',\
        name='view_map_tabular_file_form')

)

urlpatterns += patterns('apps.gis_tabular.views_delete',

    url(r'^delete-map/$', 'view_delete_tabular_map', name="view_delete_tabular_map"),
)
