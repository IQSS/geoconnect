from django import forms

from gc_apps.gis_basic_file.models import GISDataFile



class GISDataFileValidationForm(forms.ModelForm):
    class Meta:
        model = GISDataFile
        exclude = ('created', 'modified', 'dv_session_token', 'dv_file', 'gis_scratch_work_directory', 'md5', )



""" 
   filtered_qs = GMFUser.objects.filter(groups__id=3)        
        w_choices = [('', '---------')]
        for item in filtered_qs:
            w_choices.append((item.id, fmt_user_val(item)))
        self.fields['project_contact'].widget.choices = w_choices
   
"""