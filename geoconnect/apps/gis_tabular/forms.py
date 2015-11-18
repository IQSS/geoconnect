
"""
Form for:
    - Select geospatial data
    - Select column 1
    - Select column 2 (if lat/lng)
    - clean
        - column 2 optional
        - column 1 cannot be same as column 2
"""
from django import forms
from apps.worldmap_connect.jointarget_formatter import JoinTargetFormatter

'''
class DeleteMapForm(forms.Form):

    gis_data_file_md5 = forms.CharField(widget=forms.HiddenInput())
    worldmap_layer_info_md5 = forms.CharField(widget=forms.HiddenInput())
    confirmation = forms.BooleanField(label="I understand all versions of this map will be deleted from WorldMap.", initial=False)
'''
