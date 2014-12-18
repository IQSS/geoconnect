import re
import urllib

if __name__=='__main__':
    import os, sys
    DJANGO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(DJANGO_ROOT)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'geoconnect.settings.local'

from django import forms
from django.utils.translation import ugettext_lazy as _

from django.conf import settings
#from apps.classification.models import ClassificationMethod, ColorRamp
from shared_dataverse_information.layer_classification.models import ClassificationMethod, ColorRamp

from apps.worldmap_connect.worldmap_api_url_helper import CLASSIFY_LAYER_API_PATH

CLASSIFY_METHOD_CHOICES = [ (x.id, x.display_name) for x in ClassificationMethod.objects.filter(active=True) ]
CLASSIFY_STRING_METHOD_CHOICES = [ (x.id, x.display_name) for x in ClassificationMethod.objects.filter(active=True, is_string_usable=True) ]

COLOR_RAMP_CHOICES = [ (x.id, x.display_name) for x in ColorRamp.objects.filter(active=True) ]

ATTRIBUTE_VALUE_DELIMITER = '|'
FIELD_CSS_ATTRS = {'class':'form-control input-sm'} 

print 'CLASSIFY_METHOD_CHOICES', CLASSIFY_METHOD_CHOICES

class ClassifyLayerForm(forms.Form):
    """
    Evaluate classification parameters to be used for a new layer style
    """
    layer_name = forms.CharField(widget=forms.HiddenInput())
    attribute = forms.ChoiceField(choices=[(-1, 'Error: no choices available')]\
                                    , widget=forms.Select(attrs=FIELD_CSS_ATTRS)\
                                    )
    method = forms.ChoiceField(label='Classification method'\
                                , choices=CLASSIFY_METHOD_CHOICES\
                                , widget=forms.Select(attrs=FIELD_CSS_ATTRS)\
                                )
    intervals = forms.IntegerField(label='No. of intervals', initial=5, widget=forms.NumberInput(attrs=FIELD_CSS_ATTRS))
    ramp = forms.ChoiceField(label='Colors'\
                                , choices=COLOR_RAMP_CHOICES\
                                , widget=forms.Select(attrs=FIELD_CSS_ATTRS)\
                                )
    #reverse = forms.BooleanField(initial=False, widget=forms.HiddenInput())

    #startColor =forms.CharField(max_length=7, required=False)   # irregular naming convention used to match the outgoing url string
    #endColor =forms.CharField(max_length=7, required=False)      # irregular naming convention used to match the outgoing url string
    # 
    # 
    
    def __init__(self, *args, **kwargs):
        """Initialize using a WorldMapLayerInfo object
        
        """
        
        worldmap_layerinfo = kwargs.pop('worldmap_layerinfo', None)
        
        if worldmap_layerinfo is None:
            raise Exception('ClassifyLayerForm does not have a worldmap_layerinfo object')
            
        super(ClassifyLayerForm, self).__init__(*args, **kwargs)

        raw_attribute_info = worldmap_layerinfo.get_attribute_info()
        attribute_choices = ClassifyLayerForm.format_attribute_choices_for_form(raw_attribute_info)
        
        self.fields['attribute'] = forms.ChoiceField(choices=attribute_choices, widget=forms.Select(attrs=FIELD_CSS_ATTRS))
        self.fields['layer_name'].initial = worldmap_layerinfo.layer_name
        
        
    @staticmethod
    def format_attribute_choices_for_form(attr_info):
        """
        {"display_name": "Objectid", "type": "long", "name": "OBJECTID"}, 

        """        
        if attr_info is None or len(attr_info) == 0: 
            return [('-1', 'Information not found')]
        
        choice_tuples = []
        for x in attr_info:
            if not type(x) is dict: continue        # skip non dicts
            if not (x.has_key('type') and x.has_key('name') and x.has_key('display_name')): continue    # skip missing keys
            
            choice_pair = ('%s%s%s' % (x['type'],ATTRIBUTE_VALUE_DELIMITER, x['name']), x['display_name'])     # format choice
            choice_tuples.append( choice_pair)      # add choice

        if len(choice_tuples)==0:
            return [('-1', 'Information not found')]

        return choice_tuples

    @staticmethod
    def get_classify_choices():
        return ClassificationMethod.objects.filter(active=True) 


    @staticmethod
    def get_classify_non_string_choices():
        return ClassificationMethod.objects.filter(active=True, is_string_usable=False) 


    @staticmethod
    def get_classify_string_choices():
        return ClassificationMethod.objects.filter(active=True, is_string_usable=True) 

        
    def clean_ramp(self):
        color_ramp_id = self.cleaned_data.get('ramp', None)
        if color_ramp_id is None:
            raise forms.ValidationError(_('Color ramp must be specified'), code='invalid')

        try:
            color_ramp_obj = ColorRamp.objects.filter(active=True).get(pk=color_ramp_id)
        except ColorRamp.DoesNotExist:
            #raise forms.ValidationError(_('This value is not an active ColorRamp id'), code='invalid')
            raise forms.ValidationError(\
                _('This value is not an active ColorRamp id: %(value)s'),\
                params={'value': color_ramp_id },\
            )
            #raise Exception('This value is not an active ColorRamp id')

        return color_ramp_obj 
    
    def clean_method(self):
        method_id = self.cleaned_data.get('method', None)
        if method_id is None:
            raise forms.ValidationError(_('The classification method must be specified'), code='invalid')
            
        try:
            method_obj = ClassificationMethod.objects.filter(active=True).get(pk=method_id)
        except ClassificationMethod.DoesNotExist:
            raise forms.ValidationError(\
                _('This value is not an active classification id: %(value)s'),\
                params={'value': method_id },\
            )
            
        return method_obj
        
    def get_worldmap_classify_api_url(self):
        if not self.is_valid:
            return None
        
        layer_name = self.cleaned_data.get('layer_name', None)
        if layer_name is None:
            return None
            

        return CLASSIFY_LAYER_API_PATH

        #return '%s/dvn/classify-layer/%s/' % (settings.WORLDMAP_SERVER_URL, layer_name)
        

    def clean_attribute(self):
        attribute = self.cleaned_data.get('attribute', None)
        if attribute is None:
            raise forms.ValidationError(_('The attribute must be specified'), code='invalid')

        return attribute.split(ATTRIBUTE_VALUE_DELIMITER)[-1]
    
    def clean_intervals(self):
        num_bins = self.cleaned_data.get('intervals', None)
        if num_bins is None:
            raise forms.ValidationError(_('The number of intervals must be specified'), code='invalid')
        
        print 'num_bins', type(num_bins)
        if num_bins < 1:
            raise forms.ValidationError(_('The number of intervals must be 1 or greater'), code='invalid')

        if num_bins > 300:
            raise forms.ValidationError(_('The number of intervals must be less than that!'), code='invalid')

        return num_bins
        
    def clean_layer_name(self):
        """
        "geonode:my_layer_name" becomes "my_layer_name"
        "my_layer_name" stays "my_layer_name"
        """
        layer_name = self.cleaned_data.get('layer_name', None)
        if layer_name is None:
            raise forms.ValidationError(_('The layer name must be specified'), code='invalid')
            
        return layer_name.split(':')[-1]
    
    def get_params_for_display(self):
        if not self.is_valid():
            return None
            
        form_vals = self.cleaned_data.copy()
        
        
        color_ramp_obj = form_vals['ramp']
        
        params = { 'layer_name' : form_vals['layer_name']\
                    , 'attribute' : form_vals['attribute']\
                    , 'intervals' : form_vals['intervals']\
                    , 'method' :  form_vals['method'].display_name\
                    , 'ramp' :  color_ramp_obj.display_name\
                    , 'startColor' :  color_ramp_obj.start_color\
                    , 'endColor' :  color_ramp_obj.end_color\
                    , 'reverse' : False\
                }
        return params
        
    def get_params_dict_for_classification(self):
        if not self.is_valid():
            return None
            
        form_vals = self.cleaned_data.copy()
        
        
        color_ramp_obj = form_vals['ramp']
        
        params = { 'layer_name' : form_vals['layer_name']\
                    , 'attribute' : form_vals['attribute']\
                    , 'intervals' : form_vals['intervals']\
                    , 'method' :  form_vals['method'].value_name\
                    , 'ramp' :  color_ramp_obj.value_name\
                    , 'startColor' :  color_ramp_obj.start_color\
                    , 'endColor' :  color_ramp_obj.end_color\
                    , 'reverse' : False\
                    , settings.WORLDMAP_TOKEN_NAME_FOR_DV : settings.WORLDMAP_TOKEN_FOR_DATAVERSE\
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



if __name__=='__main__':
    f = ClassifyLayerForm(initial={'layer_name': 'income_abadfe'}\
                            , attribute_choices=[ (1, 'one'), (2, 'two')]\
                        )
    print f                            