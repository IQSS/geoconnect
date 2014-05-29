from django.contrib import admin
from gis_basic_file.models import GISDataFile
from gis_basic_file.forms import GISDataFileAdminForm
"""
class GISDataFileAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ('name',  )
    list_filter = ('gis_file_type', 'dataset_name', )    
    readonly_fields = ('modified', 'created', 'md5', 'test_view', 'gis_file_type')
    list_display = ('name', 'dv_username', 'dataset_name', 'gis_file_type', 'test_view'  )
admin.site.register(GISDataFile, GISDataFileAdmin)
"""

class GISDataFileAdmin(admin.ModelAdmin):
    form = GISDataFileAdminForm
    save_on_top = True
    search_fields = ['dv_username',  'datafile_label','dataset_name', 'dv_name', 'dv_file']
    list_display = ['datafile_id', 'dv_username',  'datafile_label', 'dataset_name', 'dv_name', 'dv_file', 'modified']
    list_filter = ['dv_username', 'dv_name', 'dataset_name']   
    readonly_fields = ['modified', 'created', 'md5'\
                    ,  'datafile_type', 'datafile_expected_md5_checksum']
    fieldsets = [
         ('DataFile Info', {
                  'fields': (('datafile_id', 'datafile_label', 'datafile_version' )\
                  , 'datafile_description'\
                  , ('datafile_expected_md5_checksum', 'datafile_type'))
              }),
         ('Retrieved File', {
                     'fields': ('dv_file', 'gis_scratch_work_directory' )
          }),
         ('Dataverse user', {
               'fields': ('dv_user_email', ('dv_user_id', 'dv_username'))
           }),
           ('Owning dataverse', {
               'fields': (('dv_name', 'dv_id'), )
           }),
           ('Dataset Info', {
               'fields': (('dataset_name', 'dataset_id'),  'dataset_citation')
           }),
         
          
           ('Read-Only Info', {
               'fields': ('md5',('modified', 'created') )
           }),
       ]
       
admin.site.register(GISDataFile, GISDataFileAdmin)

