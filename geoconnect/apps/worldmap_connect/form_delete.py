from django import forms
from apps.gis_basic_file.models import GISDataFile
from apps.worldmap_connect.models import WorldMapLayerInfo


class ShapefileInfoForm(forms.Form):
    
    gis_data_file_md5 = forms.CharField()
    worldmap_layer_info_md5 = forms.CharField()


    def clean_gis_data_file_md5(self):
        md5 = self.cleaned_data.get('gis_data_file_md5')

        try:
            return GISDataFile.objects.get(md5=md5)
        except GISDataFile.DoesNotExist:
            raise forms.ValidationError("GISDataFile not found")

    def clean_worldmap_layer_info_md5(self):
        
        md5 = self.cleaned_data.get('worldmap_layer_info_md5')

        try:
            return WorldMapLayerInfo.objects.get(md5=md5)
        except WorldMapLayerInfo.DoesNotExist:
            raise forms.ValidationError("WorldMapLayerInfo not found")
            