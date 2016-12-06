from django.contrib import admin
from apps.gis_basic_file.admin import GISDataFileAdmin

from apps.gis_shapefiles.models import ShapefileInfo
from apps.gis_shapefiles.admin_forms import ShapefileInfoAdminForm

from geo_utils.admin_util import make_changelist_updates


class ShapefileInfoAdmin(GISDataFileAdmin):
    form = ShapefileInfoAdminForm
    save_on_top = True
    #list_display = ('name',  'number_of_features', 'column_names', 'modified'  )

    def changelist_view(self, request, extra_context=None):
        make_changelist_updates(self, 'list_filter', ['name', 'zipfile_checked'])
        make_changelist_updates(self, 'search_fields', ['name'])
        make_changelist_updates(self, 'list_display', ['name',  'number_of_features'])
        return super(ShapefileInfoAdmin, self).changelist_view(request, extra_context)


    def get_readonly_fields(self, request, obj=None):
        # retrieve current readonly fields
        ro_fields = super(ShapefileInfoAdmin, self).get_readonly_fields(request, obj)

        # check if new field already exists, if not, add it
        if not 'extracted_shapefile_load_path' in ro_fields:
            ro_fields.append('extracted_shapefile_load_path')
        return ro_fields

    def get_fieldsets(self, request, obj=None):
        fs = super(ShapefileInfoAdmin, self).get_fieldsets(request, obj)
        sections_name = [ x[0] for x in fs if x is not None and len(x) > 0 and not x[0] == '']
        if not 'Shapefile Info' in sections_name:
            fs = [ ('Shapefile Details', {
               'fields': ('name', ('zipfile_checked',  'has_shapefile'))
                    })\
                    , ('Shapefile Info', {
                       'fields': ('number_of_features', 'column_names', 'column_info', 'extracted_shapefile_load_path', 'bounding_box')
                    })\
                 ] + fs
        return fs
admin.site.register(ShapefileInfo, ShapefileInfoAdmin)
