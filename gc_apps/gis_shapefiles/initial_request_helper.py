"""
This was previously crammed into a view--breaking it out for maintainability
"""
import json
import requests

from django.http import HttpRequest
from django.conf import settings


from gc_apps.geo_utils.template_constants import FAILED_TO_RETRIEVE_DATAVERSE_FILE,\
    FAILED_TO_CONVERT_RESPONSE_TO_JSON,\
    FAILED_BAD_STATUS_CODE_FROM_WORLDMAP,\
    FAILED_TO_IDENTIFY_METADATA_MAPPING_TYPE

from gc_apps.layer_types.static_vals import is_valid_dv_type
from gc_apps.geo_utils.error_result_msg import log_connect_error_message
import logging

LOGGER = logging.getLogger(__name__)


URL_PARAM_CALLBACK = 'cb'
DV_DATA_KEY_MAPPING_TYPE = 'mapping_type'


class InitialRequestHelper(object):
    """Dataverse requests to WorldMap have the same initial steps:
    (1) Receive request with a callback url
    (2) Make callback request for Dataverse metadata regarding:
        - The Dataverse file to map
        - The type of mapping: shapefile, tabular, geotiff, etc
        - Depending on the type of mapping, take the correct action
    """

    def __init__(self, request, dataverse_token):
        assert isinstance(request, HttpRequest), '"request" must be a HttpRequest object!'
        assert dataverse_token is not None, 'dataverse_token cannot be None'

        self.request = request
        self.dataverse_token = dataverse_token

        self.callback_url = None
        self.mapping_type = None
        self.dv_data_dict = None

        # -------------
        self.has_err = False
        self.err_msg = None
        self.err_type = None
        # -------------

        self.handle_initial_request()

    def add_err_msg(self, msg, err_type=None):
        """Add error message for use by view"""
        #LOGGER.error(msg)
        self.has_err = True
        self.err_msg = msg
        self.err_type = err_type

    def handle_initial_request(self):
        """Main method to go through steps"""

        if not self.load_callback_url():
            return False

        if not self.make_callback():
            return False

        return self.retrieve_mapping_type()


    def load_callback_url(self):
        """Retrieve the callback_url from the request
        Example of incoming url and callback ("cb") parameter:

        http://127.0.0.1:8070/shapefile/map-it/fe1b5f64adcbf2c2c4742fe5eaa0dd6887f410d02317361d9c999c2d4cdaa63e/?cb=http%3A%2F%2Flocalhost%3A8010%2Fapi%2Fworldmap%2Fdatafile%2F
        """
        import ipdb; ipdb.set_trace()

        if self.has_err:
            return False

        if not self.request.GET.has_key(URL_PARAM_CALLBACK):
            self.add_err_msg("URL must have the callback parameter: %s" % URL_PARAM_CALLBACK)
            return False

        self.callback_url = self.request.GET[URL_PARAM_CALLBACK].strip()

        # basic check, not actually checking for a valid url
        if self.callback_url == '':
            self.add_err_msg("The callback parameter was an empty string")

        return True

    def make_callback(self):
        """Make callback via a POST request"""

        if self.has_err:
            return False

        # Prepare data for request
        #
        token_data = {settings.DATAVERSE_TOKEN_KEYNAME : self.dataverse_token}

        # Make the request
        #
        try:
            r = requests.post(self.callback_url, data=json.dumps(token_data))
        except requests.exceptions.ConnectionError as exception_obj:

            err_msg = ('<p><b>Details for administrator:</b>'
                      ' Could not contact the Dataverse server:'
                      ' {0}</p>').format(self.callback_url)

            self.add_err_msg(err_msg, FAILED_TO_RETRIEVE_DATAVERSE_FILE)

            log_connect_error_message(err_msg, LOGGER, exception_obj)

            return False


        # ------------------------------
        # Check for valid status code
        # ------------------------------
        if not r.status_code == 200:
            err_msg1 = 'Status code from dataverse: %s' % (r.status_code)
            #err_msg2 = err_msg1 + '\nResponse: %s' % (r.text)
            self.add_err_msg(err_msg1, FAILED_BAD_STATUS_CODE_FROM_WORLDMAP)
            return False

        # ------------------------------
        # Attempt to convert response to JSON
        # ------------------------------
        try:
            jresp = r.json()
        except ValueError:
            err_msg1 = ('Failed to convert response to JSON\n'\
                        'Status code from dataverse: %s') % (r.status_code)
            #err_msg2 = err_msg1 + '\nResponse: %s' % (r.text)
            #LOGGER.error(err_msg2)
            self.add_err_msg(err_msg1, FAILED_TO_CONVERT_RESPONSE_TO_JSON)
            return False


        #print json.dumps(jresp, indent=4)

        # ------------------------------
        # Examine response
        #
        # (1) Identify the mapping type
        # (2) Send the file through the appropriate path
        #   - e.g. shapefile, tabular file, etc.
        # ------------------------------

        # status of "OK" or "success"?
        #
        if not (jresp.has_key('status') and jresp['status'] in ['OK', 'success']):
            self.add_err_msg('Failed to retrieve Dataverse data. (status was not "OK")')
            return False

        # Contains "data" key (good use JSON schema in future)
        #
        self.dv_data_dict = jresp.get('data', None)
        if self.dv_data_dict is None:
            self.add_err_msg('Dataverse data did not contain key: "data"')
            return False

        return True

    def retrieve_mapping_type(self):

        if self.has_err:
            return False

        # Retrieve the mapping type from the data
        #
        if not self.dv_data_dict.has_key(DV_DATA_KEY_MAPPING_TYPE):
            additional_note = ('(This will happen for Dataverse versions'\
                        ' prior to 4.3 where a mapping_type is not specified.)')
            self.add_err_msg('Dataverse data did not contain key: ""%s". (%s)'\
                    % (DV_DATA_KEY_MAPPING_TYPE, additional_note))
            return False

        # Load the mapping type
        self.mapping_type = self.dv_data_dict.pop(DV_DATA_KEY_MAPPING_TYPE, None)

        if not is_valid_dv_type(self.mapping_type):
            err_msg = ('The mapping_type for this metadata was not valid.'\
                      '  Found: %s') % self.mapping_type
            self.add_err_msg(err_msg, FAILED_TO_IDENTIFY_METADATA_MAPPING_TYPE)
            return False

        # Looks good!
        return True
