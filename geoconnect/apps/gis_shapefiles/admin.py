from django.contrib import admin
from apps.gis_basic_file.admin import GISDataFileAdmin

from apps.gis_shapefiles.models import ShapefileSet, SingleFileInfo
from apps.gis_shapefiles.admin_forms import ShapefileSetAdminForm

from geo_utils.admin_util import make_changelist_updates


class SingleFileInfoAdmin(admin.ModelAdmin ):    
    save_on_top = True
    search_fields = ('name',  )
    list_filter = ('extension',  )    
    readonly_fields = ('modified', 'created', 'md5', 'extension', 'filesize', 'is_required_shapefile', 'extracted_file_path', 'filesize_text')
    list_display = ('name',  'extension', 'filesize_text', 'is_required_shapefile', 'modified'  )
admin.site.register(SingleFileInfo, SingleFileInfoAdmin)


class ShapefileSetAdmin(GISDataFileAdmin):    
    form = ShapefileSetAdminForm
    save_on_top = True
    #list_display = ('name',  'number_of_features', 'column_names', 'modified'  )
                
    def changelist_view(self, request, extra_context=None):
        make_changelist_updates(self, 'list_filter', ['name', 'zipfile_checked'])
        make_changelist_updates(self, 'search_fields', ['name'])
        make_changelist_updates(self, 'list_display', ['name',  'number_of_features'])
        return super(ShapefileSetAdmin, self).changelist_view(request, extra_context)
    
    
    def get_readonly_fields(self, request, obj=None):
        # retrieve current readonly fields 
        ro_fields = super(ShapefileSetAdmin, self).get_readonly_fields(request, obj)

        # check if new field already exists, if not, add it
        if not 'extracted_shapefile_load_path' in ro_fields:
            ro_fields.append('extracted_shapefile_load_path')
        return ro_fields
    
    def get_fieldsets(self, request, obj=None):
        fs = super(ShapefileSetAdmin, self).get_fieldsets(request, obj)
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
admin.site.register(ShapefileSet, ShapefileSetAdmin)
