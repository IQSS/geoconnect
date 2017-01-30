from django.conf.urls import url
from gc_apps.registered_dataverse import views

urlpatterns = [

    url(r'^filetype-list/?$', views.view_filetype_list, name="view_filetype_list"),

    url(r'^filetype-note/(?P<file_type_slug>\w{4,50})/?$', views.view_filetype_note, name="view_filetype_note"),

]
