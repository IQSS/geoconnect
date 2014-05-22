from django.contrib import admin
from gis_basic_file.models import GISFileHelper, GISDataFile

class GISFileHelperAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ('name',  )
    list_filter = ('gis_file_type', 'dataset_name', )    
    readonly_fields = ('update_time', 'create_time', 'md5', 'test_view', 'gis_file_type')
    list_display = ('name', 'dv_username', 'dataset_name', 'gis_file_type', 'test_view'  )
admin.site.register(GISFileHelper, GISFileHelperAdmin)


class GISDataFileAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ('dv_username',  'datafile_name', 'datafile_type', 'dataset_name', 'dv_name', 'dv_file')
    list_filter = ('dv_username', 'dv_name', 'dataset_name')    
    readonly_fields = ('update_time', 'create_time', 'md5', )
    list_display = ('dv_username',  'datafile_name', 'dataset_name', 'dv_name', 'dv_file', 'update_time')
    fieldsets = (
           ('Dataverse user', {
               'fields': ('dv_user_id', 'dv_username',)
           }),
           ('Owning dataverse', {
               'fields': ('dv_id', 'dv_name', )
           }),
           ('Dataset Info', {
               'fields': ('dataset_id', 'dataset_name', 'dataset_citation')
           }),
           ('DataFile Info', {
               'fields': ('datafile_id', 'datafile_version', 'datafile_name', 'datafile_desc', 'datafile_type', 'datafile_expected_md5_checksum')
           }),
           ('Retrieved File', {
               'fields': ('dv_file', 'gis_scratch_work_directory' )
           }),
           ('Read-Only Info', {
               'fields': ('md5', 'update_time', 'create_time' )
           }),
       )
       
admin.site.register(GISDataFile, GISDataFileAdmin)

