from django.contrib import admin
from style_layer_information.models import BinningAlgorithm, StyleLayerDescriptionInformation

class BinningAlgorithmAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ('name', 'description')
    readonly_fields = ('update_time', 'create_time',)
    list_display = ('name', 'description')
admin.site.register(BinningAlgorithm, BinningAlgorithmAdmin)


class StyleLayerDescriptionInformationAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ('name', 'description')
    readonly_fields = ('update_time', 'create_time', 'md5')
    list_display = ('gis_file_helper', 'chosen_column', 'chosen_column', 'binning_algorithm', 'update_time')
    list_filter = ('binning_algorithm', 'gis_file_helper', )    
admin.site.register(StyleLayerDescriptionInformation, StyleLayerDescriptionInformationAdmin)
        