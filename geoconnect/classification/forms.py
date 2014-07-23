import re
import urllib

if __name__=='__main__':
    import os, sys
    DJANGO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(DJANGO_ROOT)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'geoconnect.settings.local'

from django import forms

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
    #reverse = forms.BooleanField(initial=False, required=False)

    #startColor =forms.CharField(max_length=7, required=False)   # irregular naming convention used to match the outgoing url string
    #endColor =forms.CharField(max_length=7, required=False)      # irregular naming convention used to match the outgoing url string

    


    def __init__(self, *args, **kwargs):
        attribute_choices = kwargs.pop('attribute_choices', None)
        if attribute_choices is None or len(attribute_choices) < 1:
            raise Exception('ClassifyLayerForm does not have attribute_choices')
        super(ClassifyLayerForm, self).__init__(*args, **kwargs)
        self.fields['attribute'] = forms.ChoiceField(choices=attribute_choices)


if __name__=='__main__':
    f = ClassifyLayerForm(initial={'layer_name': 'income_abadfe'}\
                            , attribute_choices=[ (1, 'one'), (2, 'two')]\
                        )
    print f                            