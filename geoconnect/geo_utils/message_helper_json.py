import json

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


