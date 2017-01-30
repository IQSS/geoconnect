from django.conf.urls import url
from gc_apps.classification import views, views_debug

urlpatterns = [

    url(r'^classify-layer/(?P<import_success_md5>\w{32})$', views.view_classify_layer_form, name="view_classify_layer_form"),

    url(r'^show-layer-links/?$', views_debug.view_show_lawyer_links, name="view_show_lawyer_links"),

]
