from django.contrib import admin
from gc_apps.style_layer_information.models import BinningAlgorithm, StyleLayerDescriptionInformation

class BinningAlgorithmAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ('name', 'description')
    readonly_fields = ('modified', 'created',)
    list_display = ('name', 'description')
admin.site.register(BinningAlgorithm, BinningAlgorithmAdmin)


class StyleLayerDescriptionInformationAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ('name', 'description')
    readonly_fields = ('modified', 'created', 'md5')
    list_display = ('gis_data_file', 'chosen_column', 'chosen_column', 'binning_algorithm', 'modified')
    list_filter = ('binning_algorithm', 'gis_data_file', )    
admin.site.register(StyleLayerDescriptionInformation, StyleLayerDescriptionInformationAdmin)
        