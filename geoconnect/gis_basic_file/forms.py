from django import forms
#from taxonomy.models import Species


class GISDataFileAdminForm(forms.ModelForm):
    #def __init__(self, *args, **kwargs):
    #    super(PlantAdminForm, self).__init__(*args, **kwargs)
    #    self.fields['species'].queryset = Species.objects.all()
    #    self.fields['species'].label_from_instance = lambda obj: "%s" % (obj.species_full_name())
    
    class Meta:
        widgets = {  'datafile_description': forms.Textarea(attrs={'rows': 2, 'cols':70})\
                , 'dataset_description': forms.Textarea(attrs={'rows': 2, 'cols':70})\
           # , 'name': forms.TextInput(attrs={'size':20}) 
            }
    """    filtered_qs = GMFUser.objects.filter(groups__id=3)        
        w_choices = [('', '---------')]
        for item in filtered_qs:
            w_choices.append((item.id, fmt_user_val(item)))
        self.fields['project_contact'].widget.choices = w_choices
    """