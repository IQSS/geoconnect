import logging

from django import forms
from apps.worldmap_layers.models import WorldMapLayerInfo
from apps.layer_types.static_vals import is_valid_dv_type
from apps.classification.utils import get_worldmap_info_object

LOGGER = logging.getLogger(__name__)


class DeleteTabularMapForm(forms.Form):

    worldmap_tab_info_md5 = forms.CharField(widget=forms.HiddenInput())
    layer_type = forms.CharField(widget=forms.HiddenInput())
    confirmation = forms.BooleanField(label="I understand all versions of this map will be deleted from WorldMap.", initial=False)

    def get_worldmap_layer_info(self):
        """
        Return the WorldMapLayerInfo object
        """
        assert self.cleaned_data is not None, "The form was not validated"

        layer_type = self.cleaned_data.get('layer_type')
        tab_md5 = self.cleaned_data.get('worldmap_tab_info_md5')

        return get_worldmap_info_object(layer_type, tab_md5)


    def clean_layer_type(self):
        """Make sure this is a valid layer type for a WorldMapLayerInfo object"""
        layer_type = self.cleaned_data.get('layer_type', None)
        if is_valid_dv_type(layer_type):
            raise forms.ValidationError("This is not a valid layer type: %s" % layer_type)

        return layer_type


    @staticmethod
    def get_form_with_initial_vals(worldmap_info):
        """
        Build an initial form using one of these objects:
            - WorldMapJoinLayerInfo
            - WorldMapLatLngInfo
        """
        assert isinstance(worldmap_info, WorldMapLayerInfo),\
            "worldmap_info must be a WorldMapLayerInfo object"

        params = dict(worldmap_tab_info_md5=worldmap_info.md5,\
                    layer_type=worldmap_info.get_layer_type()\
                 )

        delete_form = DeleteTabularMapForm(initial=params)

        return delete_form

"""
from apps.gis_tabular.models import WorldMapJoinLayerInfo, WorldMapLatLngInfo
from apps.gis_tabular.forms_delete import DeleteTabularMapForm

w = WorldMapJoinLayerInfo.objects.first()
f = DeleteTabularMapForm.get_form_with_initial_vals(w)
"""
