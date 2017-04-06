from django.contrib import admin
from gc_apps.gis_basic_file.models import GISDataFile

from shared_dataverse_information.dataverse_info.admin import DataverseInfoAdmin



class GISDataFileAdmin(DataverseInfoAdmin):
    """
    Use the ModelAdmin from DataverseInfoAdmin and extend it to include GISDataFile specific fields
    """
    search_fields =  DataverseInfoAdmin.search_fields + ['dv_file']
    readonly_fields = DataverseInfoAdmin.readonly_fields + ['md5']#, 'dv_session_token']
    list_display = DataverseInfoAdmin.list_display + ['md5', 'dv_file']

    # fieldsets: Use DataverseInfoAdmin fieldsets and add a GeoConnect specific row
    #
    fieldsets = [fs for fs in DataverseInfoAdmin.fieldsets]
    geoconnect_fieldset = ('GeoConnect specific', {'fields': ['registered_dataverse', 'dv_session_token', 'dv_file', 'gis_scratch_work_directory']})
    fieldsets.insert(0, geoconnect_fieldset)   # second to last in admin

# register the model
admin.site.register(GISDataFile, GISDataFileAdmin)
