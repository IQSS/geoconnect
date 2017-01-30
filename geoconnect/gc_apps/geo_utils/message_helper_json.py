import json
from django import forms


class MessageHelperJSON(object):

    @staticmethod
    def get_dict_msg(success=False, msg='', data_dict=None):

        if isinstance(data_dict, dict) or isinstance(data_dict, list) or isinstance(data_dict, tuple):
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
    def get_json_fail_msg(msg, data_dict=None):
        return MessageHelperJSON.get_json_msg(success=False, msg=msg, data_dict=data_dict)

    @staticmethod
    def get_json_success_msg(msg=None, data_dict=None):
        return MessageHelperJSON.get_json_msg(success=True, msg=msg, data_dict=data_dict)


    @staticmethod
    def get_json_msg(success=False, msg='', data_dict=None):

        d = MessageHelperJSON.get_dict_msg(success, msg, data_dict)
        return MessageHelperJSON.get_json_msg_from_dict(d)


"""
If a form is not valid, format the errors for a string
"""
def format_errors_as_text(form_obj, for_web=False):
    """
    Format Django form errors as text.

    RAW:
        {'dv_user_email': [u'This field is required.'], 'abstract': [u'This field is req
uired.'], 'shapefile_name': [u'This field is required.'], 'title': [u'This field
 is required.']}

    FORMATTED:
    '''
    Errors found with the following field(s):

    - dv_user_email: This field is required.

    - abstract: This field is required.

    - shapefile_name: This field is required.

    - dv_user_email: This is not a valid email address.
    '''
    :param form_obj: forms.Form, forms.ModelForm, is_valid() is False
    :return: str
    """
    assert isinstance(form_obj, forms.Form) or isinstance(form_obj, forms.ModelForm) \
        , "form_obj must be a forms.Form or a forms.ModelForm"

    assert form_obj.is_valid() is False, "The form is valid.  Expecting an invalid form with errors."

    outlines = ['Errors found with the following field(s):']

    line_break = '\n'
    tab_char = '\t'
    if for_web:
        line_break = '<br />'
        tab_char = '&nbsp; &nbsp; '

    for field_name, err_list in form_obj.errors.items():
        if field_name == '__all__':
            continue
        for idx, err_msg in enumerate(err_list):
            if idx == 0:
                outlines.append('%s- %s: %s' % (line_break, field_name, err_msg))
            else:
                outlines.append('{0}{0}{1}'.format(tab_char, err_msg))

    return line_break.join(outlines)
