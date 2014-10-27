from django.conf.urls import patterns, include, url


urlpatterns = patterns('apps.column_stats.views',

    url(r'^test/$', 'view_png_test', name="view_png_test"),

)


