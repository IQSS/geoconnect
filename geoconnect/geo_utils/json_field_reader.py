import json
import os
# logging!!!

def get_json_str_msg(success=False, msg=''):
    return { 'success': success\
            , 'message' : msg \
            }

class JSONFieldReader:
    """Convenience class used to move text values to JSON and vice-versa for Django TextFields
    """
    
    @staticmethod
    def get_json_string_as_python_val(json_string):
       """For retrieving from models.TextField"""
       try:
           return json.loads(json_string)   # JSON string -> python; e.g. '[1, 2, 3]' -> [1, 2, 3]
       except:
           return ''

    @staticmethod
    def get_python_val_as_json_string(python_val):
       """For storing in models.TextField"""
       print 'get_python_val_as_json_string', python_val
       print 'class:', python_val.__class__.__name__
       
       #return json.dumps(python_val)    # python list or dict -> JSON string

       try:
           return json.dumps(python_val)    # python list or dict -> JSON string
       except:
           return ''
 