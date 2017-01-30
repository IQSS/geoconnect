from django import forms
from gc_apps.gis_shapefiles.models import ShapefileInfo


class ShapefileInfoForm(forms.ModelForm):
    class Meta:
        model = ShapefileInfo
        exclude = ('created', 'modified', 'zipfile_checked', 'has_shapefile', 'column_names', 'column_info', 'bounding_box', 'md5', 'number_of_features', 'gis_scratch_work_directory', 'extracted_shapefile_load_path')
        #fields = ['datafile_id', 'datafile_label', 'dv_user_email', 'dv_user_id', 'dv_username', 'dv_file']
"""

class ShapefileGroupForm(forms.Form):
    name = forms.CharField(initial='BARI test')
    gis_file = forms.FileField(label='GIS file')
    #sender = forms.EmailField()
    #cc_myself = forms.BooleanField(required=False)
    
"""