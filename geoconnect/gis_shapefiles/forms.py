from django import forms
from gis_shapefiles.models import ShapefileGroup


class ShapefileGroupForm(forms.ModelForm):
    class Meta:
        model = ShapefileGroup
        fields = ['name', 'shp_file',]
"""

class ShapefileGroupForm(forms.Form):
    name = forms.CharField(initial='BARI test')
    gis_file = forms.FileField(label='GIS file')
    #sender = forms.EmailField()
    #cc_myself = forms.BooleanField(required=False)
    
"""