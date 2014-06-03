

class KeyCheckResponse:
    def __init__(self, success, missing_keys=None):
        self.success = success
        self.missing_keys = missing_keys
        self.has_missing_keys = False
        self.err_msg = None
        
        if not success and missing_keys is None:
            self.err_msg = 'The required keys were not specified'
        elif not success and type(missing_keys) in [list, tuple]:
            str_keys = ['%s' % k for k in missing_keys]
            self.err_msg = 'The following required keys were missing: %s' % str_keys
        else:
            self.err_msg = 'There was an error when checking the required keys.'
            
class KeyChecker:

    @staticmethod
    def has_required_values(required_keys, list_to_check):
        """
        Compare to lists (or tuples).  Make sure that "list_to_check" has all of the "required_keys"
     
        :param required_keys: [ ] or ( ) containing keys. e.g. ['layer_name', 'token']  or (key1, key2, etc)
        :param list_to_check: python [ ] or ( ) 
        :returns: tuple in the following format.  
            success: (True, None)   # All keys are present
            fail: (False, [missing_key1, missing_key2, etc] # return list with missing keys
            fail: (False, None) # No required keys
        """
        if not type(required_keys) in [list, tuple]:   # required_keys Not a [] or ()
            return KeyCheckResponse(False, None)
        #
        if not type(list_to_check) in [list, tuple]:     # list_to_check NOT a [] or ()
            return KeyCheckResponse(False, required_keys)      # All keys are missing
    
        # create list of missing keys
        # 
        missing_keys = [req_key for req_key in required_keys if not req_key in list_to_check ]
     
        # return missing keys, if they exist
        if len(missing_keys) > 0:
            return KeyCheckResponse(False, missing_keys)
 
        return KeyCheckResponse(True, None)

    @staticmethod
    def has_required_keys(required_keys, dict_to_check):
        """
        Check to make sure that the dict_to_check has all the required keys.  Only checks if keys exist, not if they have the correct value.
     
        :param required_keys: [ ] or ( ) containing keys. e.g. ['layer_name', 'token']  or (key1, key2, etc)
        :param dict_to_check: python dict
        :returns: tuple in the following format.  
            success: (True, None)   # All keys are present
            fail: (False, [missing_key1, missing_key2, etc] # return list with missing keys
            fail: (False, None) # No required keys
        """
        if not type(dict_to_check)== dict:     # dict_to_check NOT a dict
            return KeyCheckResponse(False, required_keys)      # All keys are missing
    
        return KeyChecker.has_required_values(required_keys, dict_to_check.keys())
    