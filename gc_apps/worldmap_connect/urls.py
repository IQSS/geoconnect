"""Convenience urls for JoinTargets"""
from django.conf.urls import url
from gc_apps.worldmap_connect import views

urlpatterns = [

    url(r'^clear-jointarget-info/$', views.clear_jointarget_info, name="clear_jointarget_info"),

    url(r'^show-jointarget-info/$', views.show_jointarget_info, name="show_jointarget_info"),

    url(r'^test-err-log/$', views.view_test_err_log, name="view_test_err_log"),

]
