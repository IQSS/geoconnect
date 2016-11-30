import json
import os

# logging!!!
from msg_util import *


class JSONFieldReader:
    """Convenience class used to move text values to JSON and vice-versa for Django TextFields
    """

    @staticmethod
    def get_json_string_as_python_val(json_string):
       """For retrieving from models.TextField"""
       return json.loads(json_string)
       try:
           return json.loads(json_string)   # JSON string -> python; e.g. '[1, 2, 3]' -> [1, 2, 3]
       except:
           return None

    @staticmethod
    def get_python_val_as_json_string(python_val):
       """For storing in models.TextField"""
       #print 'get_python_val_as_json_string', python_val

       #return json.dumps(python_val)    # python list or dict -> JSON string

       try:
           return json.dumps(python_val)    # python list or dict -> JSON string
       except:
           return ''

    @staticmethod
    def is_string_convertible_json(val):
        assert val is not None, 'val cannot be None'

        try:
            json.loads(val)
        except:
            return False
        return True
