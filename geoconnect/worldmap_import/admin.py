from django.contrib import admin

from worldmap_import.models import WorldMapImportAttempt, WorldMapImportFail, WorldMapImportSuccess

class WorldMapImportFailInline(admin.TabularInline):
    model = WorldMapImportFail
    readonly_fields = ('modified', 'created',)
    fields = ('msg', 'modified', 'created')
    extra = 0
    
class WorldMapImportSuccessInline(admin.TabularInline):
    model = WorldMapImportSuccess
    readonly_fields = ('modified', 'created',)
    fields = ('layer_name', 'layer_link', 'worldmap_username', 'modified', 'created')
    extra = 0
    
class WorldMapImportAttemptAdmin(admin.ModelAdmin):
    inlines = (WorldMapImportSuccessInline, WorldMapImportFailInline)
    save_on_top = True
    list_display = ('id', 'dv_username', 'title', 'shapefile_name', 'datafile_id', 'datafile_version', 'modified'  )
    search_fields = ('title', 'abstract', )
    list_filter = ('dv_username',  )    
    readonly_fields = ('modified', 'created',)
admin.site.register(WorldMapImportAttempt, WorldMapImportAttemptAdmin)


class WorldMapImportFailAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('import_attempt', 'msg', 'modified' )
    readonly_fields = ('modified', 'created',)
    search_fields = ('msg', 'import_attempt__title', 'import_attempt__abstract',)
admin.site.register(WorldMapImportFail, WorldMapImportFailAdmin)


class WorldMapImportSuccessAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('import_attempt', 'worldmap_username', 'layer_name', 'layer_link', 'modified' )
    readonly_fields = ('modified', 'created',)
    list_filter = ('worldmap_username', )
    search_fields = ('import_attempt__title', 'import_attempt__abstract', )
admin.site.register(WorldMapImportSuccess, WorldMapImportSuccessAdmin)
