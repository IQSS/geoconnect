from django.conf.urls import patterns, include, url

urlpatterns = patterns('gc_apps.registered_dataverse.views',
    url(r'^filetype-list/?$', 'view_filetype_list', name="view_filetype_list"),
    url(r'^filetype-note/(?P<file_type_slug>\w{4,50})/?$', 'view_filetype_note', name="view_filetype_note"),

)
