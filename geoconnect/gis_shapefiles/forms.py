from django import forms
from gis_shapefiles.models import ShapefileSet


class ShapefileSetForm(forms.ModelForm):
    class Meta:
        model = ShapefileSet
        fields = ['datafile_id', 'datafile_label', 'dv_user_email', 'dv_user_id', 'dv_username', 'dv_file']
"""

class ShapefileGroupForm(forms.Form):
    name = forms.CharField(initial='BARI test')
    gis_file = forms.FileField(label='GIS file')
    #sender = forms.EmailField()
    #cc_myself = forms.BooleanField(required=False)
    
"""