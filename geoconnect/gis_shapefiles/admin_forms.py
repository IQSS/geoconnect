from django import forms


class ShapefileSetAdminForm(forms.ModelForm):
     
    class Meta:
        widgets = {  'datafile_description': forms.Textarea(attrs={'rows': 2, 'cols':70})\
                    , 'dataset_citation': forms.Textarea(attrs={'rows': 2, 'cols':70})\
                    , 'column_names': forms.Textarea(attrs={'rows': 3, 'cols':80})\
                    , 'column_info': forms.Textarea(attrs={'rows': 3, 'cols':80})\
            }
    