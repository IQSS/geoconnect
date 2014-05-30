import json
import os

# logging!!!
from msg_util import *

class MessageHelperJSON:

    @staticmethod
    def get_dict_msg(success=False, msg='', data_dict=None):
        if type(data_dict) is dict:
            if msg:
                return { 'success': success, 'message' : msg, 'data' : data_dict }
            else:
                return { 'success': success, 'data' : data_dict }
    
        return { 'success': success, 'message' : msg }

    @staticmethod
    def get_json_msg_from_dict(dict_to_dump):

        try:        
            return json.dumps(dict_to_dump)
        except:
            return json.dumps({ 'success': False, 'message' : 'Convert to JSON message failed' })

    @staticmethod
    def get_json_msg(success=False, msg='', data_dict=None):
    
        d = MessageHelperJSON.get_dict_msg(success, msg, data_dict)
        return MessageHelperJSON.get_json_msg_from_dict(d)

 

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
       #print 'get_python_val_as_json_string', python_val
       
       #return json.dumps(python_val)    # python list or dict -> JSON string

       try:
           return json.dumps(python_val)    # python list or dict -> JSON string
       except:
           return ''
 