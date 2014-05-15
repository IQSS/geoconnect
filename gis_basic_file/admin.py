from django.contrib import admin
from gis_basic_file.models import GISFileHelper

class GISFileHelperAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ('name',  )
    list_filter = ('gis_file_type', 'dataset_name', )    
    readonly_fields = ('update_time', 'create_time', 'md5', 'test_view', 'gis_file_type')
    list_display = ('name', 'dv_username', 'dataset_name', 'gis_file_type', 'test_view'  )
admin.site.register(GISFileHelper, GISFileHelperAdmin)

