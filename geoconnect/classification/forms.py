import re
import urllib

if __name__=='__main__':
    import os, sys
    DJANGO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(DJANGO_ROOT)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'geoconnect.settings.local'

from django import forms

from django.conf import settings
from classification.models import ClassificationMethod, ColorRamp

CLASSIFY_METHOD_CHOICES = [ (x.id, x.display_name) for x in ClassificationMethod.objects.filter(active=True) ]
COLOR_RAMP_CHOICES = [ (x.id, x.display_name) for x in ColorRamp.objects.filter(active=True) ]


class ClassifyLayerForm(forms.Form):
    """
    Evaluate classification parameters to be used for a new layer style
    """
    layer_name = forms.CharField(widget=forms.HiddenInput())
    attribute = forms.ChoiceField(choices=[(-1, 'Error: no choices available')])
    method = forms.ChoiceField(choices=CLASSIFY_METHOD_CHOICES)
    intervals = forms.IntegerField(required=False)
    ramp = forms.ChoiceField(choices=COLOR_RAMP_CHOICES)
    #reverse = forms.BooleanField(initial=False, widget=forms.HiddenInput())

    #startColor =forms.CharField(max_length=7, required=False)   # irregular naming convention used to match the outgoing url string
    #endColor =forms.CharField(max_length=7, required=False)      # irregular naming convention used to match the outgoing url string

    def clean_ramp(self):
        color_ramp_id = self.cleaned_data.get('ramp', None)
        if color_ramp_id is None:
            raise Exception('Color ramp must be specified')

        try:
            color_ramp_obj = ColorRamp.objects.filter(active=True).get(pk=color_ramp_id)
        except ColorRamp.DoesNotExist:
            raise Exception('This value is not an active ColorRamp id')

        return color_ramp_obj 
    
    def clean_method(self):
        method_id = self.cleaned_data.get('method', None)
        if method_id is None:
            raise Exception('Color ramp must be specified')

        try:
            method_obj = ClassificationMethod.objects.filter(active=True).get(pk=method_id)
        except ClassificationMethod.DoesNotExist:
            raise Exception('This value is not an active ColorRamp id')

        return method_obj
        
    def get_worldmap_classify_api_url(self):
        if not self.is_valid:
            return None
        
        layer_name = self.cleaned_data.get('layer_name', None)
        if layer_name is None:
            return None
            

        return '%s/dvn/classify-layer/' % (settings.WORLDMAP_SERVER_URL)

        #return '%s/dvn/classify-layer/%s/' % (settings.WORLDMAP_SERVER_URL, layer_name)
        
    
    def clean_layer_name(self):
        layer_name = self.cleaned_data.get('layer_name', None)
        if layer_name is None:
            raise Exception('Color ramp must be specified')

        return layer_name.split(':')[-1]
        
    def get_params_dict_for_classification(self):
        if not self.is_valid:
            return None
            
        form_vals = self.cleaned_data.copy()
        
        
        color_ramp_obj = form_vals['ramp']
        
        params = { 'layer_name' : form_vals['layer_name']\
                    , 'intervals' : form_vals['intervals']\
                    , 'method' :  form_vals['method'].value_name\
                    , 'ramp' :  color_ramp_obj.value_name\
                    , 'startColor' :  color_ramp_obj.start_color\
                    , 'endColor' :  color_ramp_obj.end_color\
                    , 'reverse' : False\
                    , 'geoconnect_token' : settings.WORLDMAP_TOKEN_FOR_DV\
                }
        return params
        """
        layer_name = forms.CharField(max_length=255)
        attribute = forms.CharField(max_length=100)
        method = forms.ChoiceField(choices=CLASSIFY_METHOD_CHOICES)
        intervals = forms.IntegerField(required=False)
        ramp = forms.ChoiceField(choices=COLOR_RAMP_CHOICES)
        reverse = forms.BooleanField(initial=False, required=False)

        startColor =forms.CharField(max_length=7, required=False)   # irregular naming convention used to match the outgoing url string
        endColor =forms.CharField(max_length=7, required=False)      # irregular naming convention used to match the outgoing url string
        """


    def __init__(self, *args, **kwargs):
        """Initialize using a WorldMapImportSuccess object
        
        """
        
        import_success_object = kwargs.pop('import_success_object', None)
        
        if import_success_object is None:
            raise Exception('ClassifyLayerForm does not have an import_success_object')
            
        super(ClassifyLayerForm, self).__init__(*args, **kwargs)

        self.fields['attribute'] = forms.ChoiceField(choices=import_success_object.get_attribute_choices_for_form())
        self.fields['layer_name'].initial = import_success_object.layer_name

if __name__=='__main__':
    f = ClassifyLayerForm(initial={'layer_name': 'income_abadfe'}\
                            , attribute_choices=[ (1, 'one'), (2, 'two')]\
                        )
    print f                            