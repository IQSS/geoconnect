import json
import os

# logging!!!
from msg_util import *

from jsonfield.encoder import JSONEncoder as JSONExtraEncoder
#from geo_utils.json_encoder import JSONExtraEncoder


class JSONHelper:
    """Convenience class used to move text values to JSON and vice-versa for Django TextFields
    """

    @staticmethod
    def is_py_obj_encodable(obj):
        """Used for checking if a python object is JSON encodable.
        3rd party encoder checks date/time/timedelta,
        decimal types, generators and other basic python objects"""

        try:
            JSONExtraEncoder().encode(obj)
            return True
        except:
            return False

    @staticmethod
    def to_python_or_none(json_string):
        """For data received via API that we want to store in a jsonfield.JSONField
        An example would be the data regarding a new TableJoin

        1st check if the string can be load to a python object.
        Note: This will (or at least should) be replaced by using JSON schema
        """
        try:
            return json.loads(json_string)
        except:
            return None

    @staticmethod
    def to_python(json_string):
        return JSONHelper.get_json_string_as_python_val(json_string)

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
