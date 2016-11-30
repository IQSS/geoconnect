from django.contrib import admin

from apps.worldmap_connect.models import WorldMapImportAttempt,\
    WorldMapImportFail, WorldMapLayerInfo,\
    JoinTargetInformation
#, APIValidationSchema

class WorldMapImportFailInline(admin.TabularInline):
    model = WorldMapImportFail
    readonly_fields = ('modified', 'created',)
    fields = ('msg', 'modified', 'created')
    extra = 0

class WorldMapLayerInfoInline(admin.TabularInline):
    model = WorldMapLayerInfo
    readonly_fields = ('modified', 'created', 'update_dataverse',  'dv_params')
    fields = ('layer_name', 'layer_link', 'embed_map_link', 'worldmap_username', 'dv_params', 'modified', 'created')
    extra = 0



class WorldMapImportAttemptAdmin(admin.ModelAdmin):
    inlines = (WorldMapLayerInfoInline, WorldMapImportFailInline)
    save_on_top = True
    list_display = ('id', 'dv_username', 'title', 'shapefile_name', 'edit_shapefile', 'datafile_id', 'dataset_version_id', 'modified'  )
    search_fields = ('title', 'abstract', )
    list_filter = ('dv_username',  )
    readonly_fields = ('modified', 'created', 'edit_shapefile')


class WorldMapImportFailAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('import_attempt', 'msg', 'modified' )
    readonly_fields = ('modified', 'created',)
    search_fields = ('msg', 'import_attempt__title', 'import_attempt__abstract',)


class WorldMapLayerInfoAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('import_attempt', 'worldmap_username', 'layer_name', 'layer_link', 'modified', 'dv_params' )
    readonly_fields = ('modified', 'created', 'md5', 'update_dataverse', 'dv_params')
    list_filter = ('worldmap_username', )
    search_fields = ('import_attempt__title', 'import_attempt__abstract', )


class JoinTargetInformationAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('name', 'created', 'modified')

'''
class APIValidationSchemaAdmin(admin.ModelAdmin):
    """May be used to evaluate API results such as APIValidationSchema"""
    save_on_top = True
    list_display = ('name', 'notes', 'created', 'modified')
'''

admin.site.register(WorldMapImportAttempt, WorldMapImportAttemptAdmin)
admin.site.register(WorldMapImportFail, WorldMapImportFailAdmin)
admin.site.register(WorldMapLayerInfo, WorldMapLayerInfoAdmin)
admin.site.register(JoinTargetInformation, JoinTargetInformationAdmin)
#admin.site.register(APIValidationSchema, APIValidationSchemaAdmin)
