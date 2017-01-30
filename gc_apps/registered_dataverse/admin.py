from django.contrib import admin

from gc_apps.registered_dataverse.models import RegisteredDataverse,\
    IncomingFileTypeSetting



class RegisteredDataverseAdmin(admin.ModelAdmin):
    search_fields = ('name', 'dataverse_url', 'notes')
    list_display = ('name', 'dataverse_url', 'active', 'notes')
    save_on_top = True
    list_filter  = ('active', )
admin.site.register(RegisteredDataverse, RegisteredDataverseAdmin)

class IncomingFileTypeSettingAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name', 'active', 'slug', 'modified')
    save_on_top = True
    list_filter  = ('active', )
admin.site.register(IncomingFileTypeSetting, IncomingFileTypeSettingAdmin)
