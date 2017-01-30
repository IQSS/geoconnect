from django.conf.urls import url
from gc_apps.column_stats import views

urlpatterns = [
    url(r'^test/$', views.view_png_test, name="view_png_test"),
]
