from django.contrib import admin
from style_layer_information.models import BinningAlgorithm, StyleLayerDescriptionInformation

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
    list_display = ('gis_file_helper', 'chosen_column', 'chosen_column', 'binning_algorithm', 'modified')
    list_filter = ('binning_algorithm', 'gis_file_helper', )    
admin.site.register(StyleLayerDescriptionInformation, StyleLayerDescriptionInformationAdmin)
        