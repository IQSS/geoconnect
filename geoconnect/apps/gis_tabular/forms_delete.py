import logging

from django import forms
from apps.gis_tabular.models import TabularFileInfo,\
                                    WorldMapJoinLayerInfo,\
                                    WorldMapLatLngInfo

LOGGER = logging.getLogger(__name__)

class DeleteTabularMapForm(forms.Form):

    worldmap_tab_info_md5 = forms.CharField(widget=forms.HiddenInput())
    is_join_layer = forms.BooleanField(widget=forms.HiddenInput, required=False)
    confirmation = forms.BooleanField(label="I understand all versions of this map will be deleted from WorldMap.", initial=False)

    def get_worldmap_layer_info(self):
        """
        Return the WorldMapLayerInfo object
        """
        assert self.cleaned_data is not None, "The form was not validated"

        is_join_layer = self.cleaned_data.get('is_join_layer')
        tab_md5 = self.cleaned_data.get('worldmap_tab_info_md5')

        if is_join_layer:
            return WorldMapJoinLayerInfo.objects.get(md5=tab_md5).first()
        else:
            return WorldMapLatLngInfo.objects.get(md5=tab_md5).first()

    @staticmethod
    def get_form_with_initial_vals(worldmap_info):
        """
        Build an initial form using one of these objects:
            - WorldMapJoinLayerInfo
            - WorldMapLatLngInfo
        """
        assert isinstance(worldmap_info, WorldMapJoinLayerInfo) or\
            isinstance(worldmap_info, WorldMapLatLngInfo),\
            "worldmap_info must be a WorldMapJoinLayerInfo or WorldMapLatLngInfo"

        params = dict(worldmap_tab_info_md5=worldmap_info.md5,\
                    is_join_layer=worldmap_info.is_join_layer()\
                 )

        delete_form = DeleteTabularMapForm(initial=params)

        return delete_form

"""
from apps.gis_tabular.models import WorldMapJoinLayerInfo, WorldMapLatLngInfo
from apps.gis_tabular.forms_delete import DeleteTabularMapForm

w = WorldMapJoinLayerInfo.objects.first()
f = DeleteTabularMapForm.get_form_with_initial_vals(w)
"""
