from django import forms


class ShapefileInfoAdminForm(forms.ModelForm):
     
    class Meta:
        widgets = {  'datafile_description': forms.Textarea(attrs={'rows': 2, 'cols':70})\
                    , 'dataset_description': forms.Textarea(attrs={'rows': 2, 'cols':70})\
                    , 'column_names': forms.Textarea(attrs={'rows': 3, 'cols':80})\
                    , 'column_info': forms.Textarea(attrs={'rows': 3, 'cols':80})\
            }
    