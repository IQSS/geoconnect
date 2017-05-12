from django.contrib import admin
from gc_apps.content_pages.models import MaintenanceMode


class MaintenanceModeAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('name', 'is_active',
                    'end_datetime', 'message',
                    'created', 'modified')

admin.site.register(MaintenanceMode, MaintenanceModeAdmin)
