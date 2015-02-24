from django.contrib import admin

from apps.registered_dataverse.models import RegisteredDataverse



class RegisteredDataverseAdmin(admin.ModelAdmin):
    list_display = ('name', 'dataverse_url', 'active', 'notes')
    save_on_top = True
admin.site.register(RegisteredDataverse, RegisteredDataverseAdmin)
