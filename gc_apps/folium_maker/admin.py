from django.contrib import admin

from .models import FoliumMap


class FoliumMapAdmin(admin.ModelAdmin ):    
    save_on_top = True
    search_fields = ('name',  )
    list_filter = ('gis_data_file',  )    
    readonly_fields = ('modified', 'created', )
    list_display = ('id',  'name', 'gis_data_file', 'folium_output_directory', 'modified'  )
admin.site.register(FoliumMap, FoliumMapAdmin)
