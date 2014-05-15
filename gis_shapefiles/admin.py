from django.contrib import admin
from gis_shapefiles.models import ShapefileGroup, SingleShapefileSet, SingleFileInfo


class ShapefileGroupAdmin(admin.ModelAdmin):    
    save_on_top = True
    search_fields = ('name',  )
    #list_filter = ('name', 'successful_database_load', )    
    readonly_fields = ('update_time', 'create_time', 'md5', 'test_view', )
    list_display = ('name',  'dv_username',  'shp_file', 'test_view','update_time'  )
admin.site.register(ShapefileGroup, ShapefileGroupAdmin)


class SingleFileInfoAdmin(admin.ModelAdmin):    
    save_on_top = True
    search_fields = ('name',  )
    list_filter = ('extension',  )    
    readonly_fields = ('update_time', 'create_time', 'md5', 'extension', 'filesize', 'is_required_shapefile', 'extracted_file_path', 'filesize_text')
    list_display = ('name',  'extension', 'filesize_text', 'is_required_shapefile', 'update_time'  )
admin.site.register(SingleFileInfo, SingleFileInfoAdmin)


class SingleShapefileSetAdmin(admin.ModelAdmin):    
    save_on_top = True
    search_fields = ('name',  )
    #list_filter = ('name', 'successful_database_load', )    
    readonly_fields = ('update_time', 'create_time', 'md5', 'extracted_shapefile_load_path')
    list_display = ('name',  'shapefile_group', 'number_of_features', 'column_names', 'update_time'  )
admin.site.register(SingleShapefileSet, SingleShapefileSetAdmin)


