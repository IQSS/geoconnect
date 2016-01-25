from django.contrib import admin
from apps.gis_basic_file.admin import GISDataFileAdmin

from apps.gis_tabular.models import TabularFileInfo
from apps.gis_tabular.models import SimpleTabularTest   # for testing

from apps.gis_tabular.admin_forms import TabularInfoAdminForm

from geo_utils.admin_util import make_changelist_updates


class SimpleTabularTestAdmin(admin.ModelAdmin):
    """For testing"""

    readonly_fields = ('delimiter',)
    list_display = ('name', 'test_page', 'dv_file', 'delimiter')
    save_on_top = True


class TabularFileInfoAdmin(GISDataFileAdmin):
    form = TabularInfoAdminForm
    save_on_top = True

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
                            'chosen_column', 'chosen_column_type')
                    })\
                 ] + fs
        return fs


admin.site.register(TabularFileInfo, TabularFileInfoAdmin)
admin.site.register(SimpleTabularTest, SimpleTabularTestAdmin)
