from django.contrib import admin

from gc_apps.worldmap_connect.models import JoinTargetInformation

class JoinTargetInformationAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('name', 'created', 'modified')

admin.site.register(JoinTargetInformation, JoinTargetInformationAdmin)
