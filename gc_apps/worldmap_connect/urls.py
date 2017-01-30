from django.conf.urls import url
from gc_apps.worldmap_connect import views

urlpatterns = [

    url(r'^clear-jointarget-info/$', views.clear_jointarget_info, name="clear_jointarget_info"),

]
