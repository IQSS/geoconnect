#### Allow ```delimiter_type``` and ```no_header_row``` parameters

##### Example change to ```UploadDataTableForm```

```python
from django import forms
from django.utils.translation import ugettext as _

"""
Specify Data Table Delimiter Choices
"""
#   Delimiter choices
#   For each delimiter, specify a "varname", "value", and "friendly_name"
#
DELIMITER_TYPE_INFO = ( dict(varname='COMMA', value=',', friendly_name='Comma Separated (.csv)'),
                        dict(varname='TAB', value='\t', friendly_name='Tab Separated (.tab)'),
                    )
assert len(DELIMITER_TYPE_INFO) > 1, "DELIMITER_TYPE_INFO must have at least one value"

DELIMITER_TYPE_CHOICES = [ (dt['varname'], dt['friendly_name']) for dt in DELIMITER_TYPE_INFO] # choices for Form
DELIMITER_VALUE_LOOKUP = dict( (dt['varname'], dt['value']) for dt in DELIMITER_TYPE_INFO)  # value look up for form "clean"
DEFAULT_DELIMITER = DELIMITER_TYPE_INFO[0]['varname']   # form default value

class UploadDataTableForm(forms.Form):
    title = forms.CharField(max_length=255)
    uploaded_file = forms.FileField()
    delimiter_type = forms.ChoiceField(choices=DELIMITER_TYPE_CHOICES, initial=DEFAULT_DELIMITER)
    no_header_row = forms.BooleanField(initial=False, required=False)   


    def clean_delimiter_type(self):
        """
        Return actual delimiter value.  e.g. form may have "COMMA" but return ","
        """
        delim = self.cleaned_data.get('delimiter_type', None)
        if delim is None:
            raise forms.ValidationError(_('delimiter_type is required'))

        delim_value = DELIMITER_VALUE_LOOKUP.get(delim, None)
        if delim_value is None:
            raise forms.ValidationError(_('Invalid value'))
            
        return delim_value
```


### ```no_header_row``` in datatables.utils

- table.from_csv - map value to ```no_header_row``` param
   - https://github.com/jj0hns0n/geonode/blob/table-join/geonode/contrib/datatables/utils.py#L46
   - Example: 
   ```
   csv_table = table.Table.from_csv(f\
                   , name=table_name\
                   , no_header_row=no_header_row\
                   )
   ```
- csvkit, use of ```no_header_row``` param:
   - https://github.com/onyxfish/csvkit/blob/master/csvkit/table.py#L190

### ```delmiter_type```

- May be able to pass in kwargs (not tested).  Example where ```chosen_delimiter``` is from api request:
```
csv_table = table.Table.from_csv(f\
                , name=table_name\
                , no_header_row=no_header_row\
                , kwargs={ 'delimiter' : chosen_delimiter}\
                )
```

#### how ```**kwargs``` appears to be passed through to python's csv library
1.  csvkit.table takes a ```**kwargs``` argument
1.  **```CSVKitReader```**: passes ```**kwargs``` to CSVKitReader: ```CSVKitReader(f, **kwargs)```
    - source: https://github.com/onyxfish/csvkit/blob/master/csvkit/table.py#L210
1.  In python 2, ```CSVKitReader``` is ```unicsv.UnicodeCSVReader```
    - source: https://github.com/onyxfish/csvkit/blob/master/csvkit/__init__.py
1.  In ```unicsv.UnicodeCSVReader```, ```**kwargs``` passed to python's ```csv.reader``` in ```csv.reader(f, **kwargs)```
    - source: https://github.com/onyxfish/csvkit/blob/master/csvkit/unicsv.py
