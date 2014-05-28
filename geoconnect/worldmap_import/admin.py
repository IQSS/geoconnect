from django.contrib import admin

from worldmap_import.models import WorldMapImportAttempt, WorldMapImportFail, WorldMapImportSuccess


class WorldMapImportAttemptAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('dv_username', 'title', 'shapefile_name', 'dataset_id', 'dataset_version_id', 'modified'  )
    search_fields = ('title', 'abstract', )
    list_filter = ('dv_username',  )    
    readonly_fields = ('modified', 'created',)
admin.site.register(WorldMapImportAttempt, WorldMapImportAttemptAdmin)


class WorldMapImportFailAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('import_attempt', 'msg', 'modified' )
    readonly_fields = ('modified', 'created',)
    search_fields = ('msg')
admin.site.register(WorldMapImportFail, WorldMapImportFailAdmin)


class WorldMapImportSuccessAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('import_attempt', 'worldmap_username', 'layer_name', 'layer_link', 'modified' )
    readonly_fields = ('modified', 'created',)
    list_filter = ('worldmap_username', )
    search_fields = ('import_attempt ')
admin.site.register(WorldMapImportSuccess, WorldMapImportSuccessAdmin)
