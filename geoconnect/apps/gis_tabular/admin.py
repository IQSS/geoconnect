from django.contrib import admin
from apps.gis_basic_file.admin import GISDataFileAdmin

from apps.gis_tabular.models import TabularFileInfo,\
                                    WorldMapJoinLayerInfo,\
                                    WorldMapLatLngInfo

from apps.gis_tabular.admin_forms import TabularInfoAdminForm

from geo_utils.admin_util import make_changelist_updates


class WorldMapLatLngInfoInline(admin.TabularInline):
    model = WorldMapLatLngInfo
    extra = 0

class WorldMapJoinLayerInfoInline(admin.TabularInline):
    model = WorldMapJoinLayerInfo
    extra = 0


class TabularFileInfoAdmin(GISDataFileAdmin):
    form = TabularInfoAdminForm
    save_on_top = True
    inlines = (WorldMapLatLngInfoInline, WorldMapJoinLayerInfoInline)

    def changelist_view(self, request, extra_context=None):
        make_changelist_updates(self, 'list_filter', ['name', 'has_header_row'])
        make_changelist_updates(self, 'search_fields', ['name'])
        make_changelist_updates(self, 'list_display', ['name',  'num_rows', 'num_columns'])
        return super(TabularFileInfoAdmin, self).changelist_view(request, extra_context)

    def get_fieldsets(self, request, obj=None):
        fs = super(TabularFileInfoAdmin, self).get_fieldsets(request, obj)
        sections_name = [ x[0] for x in fs if x is not None and len(x) > 0 and not x[0] == '']
        if not 'Shapefile Info' in sections_name:
            fs = [ ('Tabular Details', {
               'fields': ('name', ('is_file_readable',  'delimiter'))
                    })\
                    , ('Tabular Info', {
                       'fields': (('num_rows', 'num_columns'),\
                            'has_header_row', 'column_names',\
                            'chosen_column', 'dv_join_file')
                    })\
                 ] + fs
        return fs



class WorldMapTabularLayerInfoAdmin(admin.ModelAdmin):
    """
    Used for displaying two models:
        - LatLngLayerInfo
        - WorldMapTabularLayerInfoAdmin
    """
    readonly_fields = ('created', 'modified',)# 'is_join_layer', 'is_lat_lng_layer')
    list_display = ('tabular_info', 'layer_name', 'created',)# 'dv_file', 'delimiter')
    save_on_top = True

admin.site.register(TabularFileInfo, TabularFileInfoAdmin)
admin.site.register(WorldMapLatLngInfo, WorldMapTabularLayerInfoAdmin)
admin.site.register(WorldMapJoinLayerInfo, WorldMapTabularLayerInfoAdmin)
