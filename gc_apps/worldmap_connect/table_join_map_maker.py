"""Use the WorldMap API to upload a datatable and join it to an existing layer"""

import sys
import json
import pprint
import logging
import requests

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from requests.exceptions import ConnectionError as RequestsConnectionError
from csv import QUOTE_NONNUMERIC
from gc_apps.geo_utils.msg_util import msg
from gc_apps.geo_utils.tabular_util import get_formatted_column_name

from shared_dataverse_information.worldmap_api_helper.url_helper import\
    UPLOAD_JOIN_DATATABLE_API_PATH

from gc_apps.worldmap_connect.utils import get_latest_jointarget_information

# If a column needs formatting
import pandas as pd
import numpy as np

LOGGER = logging.getLogger('gc_apps.worldmap_connect.join_layer_service')


class TableJoinMapMaker(object):
    """
    Use the WorldMap API to upload a datatable and join it to an existing layer

    tj_map_maker = TableJoinMapMaker(tabular_info, dataverse_metadata_dict,
                                    chosen_column_name, chosen_layer_name)
    success = tj_map_maker.run_map_create()
    if success:
        map_info_dict = tj_map_maker.get_map_info()
    else:
        err_msg = tj_map_maker.get_error_msg()
    """
    def __init__(self, datatable_obj, dataverse_metadata_dict,\
        table_attribute_for_join, target_layer_id):
        self.datatable_obj = datatable_obj
        self.dataverse_metadata_dict = dataverse_metadata_dict
        self.table_attribute_for_join = table_attribute_for_join
        self.target_layer_id = target_layer_id

        # If a new join column is needed
        self.formatted_file_created = False
        self.zero_pad_length = None

        # For error messages
        self.err_found = False
        self.err_messages = []

        self.rjson_output = None

        self.sanity_check()
        #self.run_map_create()

    def get_map_info(self):
        """Get "data" value from JSON"""

        if self.rjson_output is None:
            return None

        if not 'data' in self.rjson_output:
            return None

        # In the prep process, was a new column/created formatted?
        if self.was_formatted_file_created():
            # Add a "was_formatted_column_created" attribute
            self.rjson_output['data']['was_formatted_column_created'] = True

            # If used, add a zero_pad_length attribute
            if self.zero_pad_length is not None:
                self.rjson_output['data']['zero_pad_length'] = self.zero_pad_length

        return self.rjson_output

    def add_error(self, err_msg):
        """
        Error detected, store a messsage in the class
        """
        if err_msg is None:
            return
        self.err_found = True
        self.err_messages.append(err_msg)

    def get_error_msg(self):
        """Return error message"""
        return '\n'.join(self.err_messages)

    def sanity_check(self):
        """Make sure objects are not None, have expected values"""

        if self.datatable_obj is None:
            self.add_error('The Tabular File object was not specified.')

        if self.dataverse_metadata_dict is None:
            self.add_error('The Dataverse metadata was not specified.')

        if self.table_attribute_for_join is None:
            self.add_error('The join column was not specified.')

        if self.target_layer_id is None:
            self.add_error('The target layer was not specified.')

        if not hasattr(self.datatable_obj, 'name'):
            self.add_error('The target layer column was not specified')

        if not hasattr(self.datatable_obj, 'delimiter'):
            self.add_error('The Tabular File object does not have a "delimiter"')


    def is_formatted_column_needed(self, data_frame, single_join_target_info):
        """
        This is called by "format_data_table_for_join" -- it is only called
        when the target column is a string and/or specifies zero-padding

        Selected join column needs formatting if:
            (a) It is type numeric
            (b) The values do not meet the minimal length (zero padding)
        """
        assert isinstance(data_frame, pd.DataFrame),\
            "data_frame must be a pandas DataFrame object"

        df = data_frame

        # --------------------------------------------
        # (1) Is this a numeric column?
        # If so, we need a formatted column b/c we're matching against a string.
        # --------------------------------------------
        col_dtype = df[self.table_attribute_for_join].dtype
        if np.isreal(col_dtype) and col_dtype != 'object':
            return True

        #   Our chosen column is character but the target doesn't have
        #   a zero padding requirement
        #
        if not single_join_target_info.requires_zero_padding():
            return False

        # --------------------------------------------
        # (2) Are the values in our column the correct length for a join?
        # --------------------------------------------
        total_rows = len(df)

        # Count how many columns meet the padding length
        #   - convert our temp column to a string
        # --------------------------------------------
        temp_col = self.table_attribute_for_join + '_temp'
        df[temp_col] = df[self.table_attribute_for_join].astype('str')

        #   - Make a filter to count how many values have
        #       the correct length
        # --------------------------------------------
        filter_criteria = (df[temp_col].str.len() == single_join_target_info.zero_pad_length)
        num_short_rows = len(df.loc[filter_criteria])

        # Drop the temp column
        df = df.drop(temp_col, axis=1)


        #   - Are all the rows the right length?
        # --------------------------------------------
        if num_short_rows == total_rows:    # Yes
            # Looks ok, no formatting needed
            return False

        # We need a formatted column
        return True



    def format_data_table_for_join(self, single_join_target_info):
        """
        Create a new file and add a formatted column that's zero-padded

        When to format a column:
            - selected column is numeric and target is string
            - target column indicates 0-padding

        Formatting consists of:
            - creating a *new*, formatted column and
            - making new column the join column
        """
        if single_join_target_info is None:
            self.add_error('single_join_target_info cannot be None')
            return False

        # Set instance wide value for zero_pad_length
        #
        zero_pad_length = single_join_target_info.zero_pad_length

        # ----------------------------------------
        # Do we need to do any formatting at all?  (Looking at the target only)
        # ----------------------------------------
        if not single_join_target_info.does_join_column_potentially_need_formatting():
            return True

        # ----------------------------------------
        # Make sure the file is still around
        # ----------------------------------------
        if not self.datatable_obj.dv_file or\
            not default_storage.exists(self.datatable_obj.dv_file.name):
            self.add_error("The file could not be found.")
            return False

        # ----------------------------------------
        # Cleanup: remove any old join files from the TabularInfo object
        # ----------------------------------------
        if self.datatable_obj.dv_join_file:
            self.datatable_obj.dv_join_file.delete()

        # ============================================
        # (1) Do we need a formatted column?
        #   - Check the type of the selected column
        # ============================================

        # --------------------------------------------
        # (1a) Open the dataverse tabular file with pandas
        # --------------------------------------------
        try:
            df = pd.read_csv(self.datatable_obj.dv_file,\
                        sep=self.datatable_obj.delimiter,\
                        )
        except pd.parser.CParserError as ex_obj:
            err_msg = ('Could not process the file. '
                       'At least one row had too many values. '
                       '(error: {0})').format(ex_obj.message)
            self.add_error(err_msg)
            return False

        # --------------------------------------------
        # (1b) Is the join column in the data frame?
        # --------------------------------------------
        if not self.table_attribute_for_join in df.columns:
            self.add_error('Failed to find column "%s" for formatting.'\
                % self.table_attribute_for_join)
            return False

        # --------------------------------------------
        # (1c) Do we need a formatted column?
        #   The data may already be formatted
        # --------------------------------------------
        if not self.is_formatted_column_needed(df, single_join_target_info):
            # The existing column may be used for the join
            return True

        # Looks like we need a formatted column

        # ----------------------------------
        # (2) Add formatted column
        # ----------------------------------
        # new column name = existing name + "_formatted"
        new_column_name = get_formatted_column_name(self.table_attribute_for_join)

        # What type of column formatting?
        #
        if single_join_target_info.requires_zero_padding():
            #
            # zero pad formatting
            #
            zero_pad_fmt = '{0:0>%s}' % zero_pad_length
            func_col_fmt = lambda x: zero_pad_fmt.format(x)
        elif single_join_target_info.is_target_column_string():
            #
            # simple convert to string
            #
            func_col_fmt = lambda x: '%s' % x

        # make the column
        # ----------------------------------
        df[new_column_name] = df[self.table_attribute_for_join].apply(\
                                lambda x: func_col_fmt(x))

        # (2b) set new join column name
        # ----------------------------------
        self.table_attribute_for_join = new_column_name

        # ----------------------------------
        # (3) Save  new file
        # ----------------------------------
        #msg('columns 4: %s' % df.columns)

        # Write the DataFrame to a ContentFile
        #
        csv_parms = dict(sep=str(self.datatable_obj.delimiter),\
                        quoting=QUOTE_NONNUMERIC,\
                        index=False,\
                        columns=df.columns,\
                        )
        content_file = ContentFile(df.to_csv(**csv_parms))

        # Save the ContentFile in the datatable_obj
        # ----------------------------------
        self.datatable_obj.dv_join_file.save(\
                self.datatable_obj.datafile_label,\
                content_file)

        # Indicate that a formatted file has been created
        # ----------------------------------
        self.formatted_file_created = True

        return True

    def was_formatted_file_created(self):
        """
        Return the flag to indicate that a new formatted file was created
        """
        return self.formatted_file_created

    def get_file_params(self):
        """
        Return file params for the WorldMap API call
        """
        if self.err_found:
            return None

        if self.was_formatted_file_created():
            return self.really_get_file_params(self.datatable_obj.dv_join_file)
        else:
            return self.really_get_file_params(self.datatable_obj.dv_file)


    def really_get_file_params(self, file_field):

        if not hasattr(file_field, 'read'):
            self.add_error('Failed to open file. FileField required.')
            return None

        file_handler = file_field   #open(file_field.path, 'rb')

        return {'uploaded_file': file_handler}


    def run_map_create(self):
        """
        Format parameters and make a WorldMap API call
        """
        if self.err_found:
            return False

        # -------------------------------------------
        # Based on the target layer ID,
        # Retrieve the layer name, column name, and zero_pad_length
        # -------------------------------------------
        all_join_target_info = get_latest_jointarget_information()

        single_join_target_info =\
            all_join_target_info.get_single_join_target_info(self.target_layer_id)

        if single_join_target_info is None:
            self.add_error('Failed to retrieve target layer information.')
            return False

        #single_join_target_info.show()

        # Update instance info
        #
        self.zero_pad_length = single_join_target_info.zero_pad_length

        # --------------------------------------------------
        # Do we need to format the data in the join column?
        # --------------------------------------------------
        format_success = self.format_data_table_for_join(single_join_target_info)
        if not format_success:
            return False


        # --------------------------------
        # Prepare parameters
        # --------------------------------
        map_params = dict(\
                    title=self.datatable_obj.name,
                    abstract=self.datatable_obj.get_abstract_for_worldmap(),
                    delimiter=self.datatable_obj.delimiter,
                    table_attribute=self.table_attribute_for_join,
                    layer_name=single_join_target_info.target_layer_name,
                    layer_attribute=single_join_target_info.target_column_name)

        # Add dataverse dict info
        #
        map_params.update(self.dataverse_metadata_dict)

        pp = pprint.PrettyPrinter(indent=4)
        msg(pp.pprint(map_params))

        # --------------------------------
        # Prepare file
        # --------------------------------
        file_params = self.get_file_params()
        if file_params is None:
            return False

        print 'make request to', UPLOAD_JOIN_DATATABLE_API_PATH
        print '-' * 40

        try:
            r = requests.post(\
                            UPLOAD_JOIN_DATATABLE_API_PATH,
                            data=map_params,
                            files=file_params,
                            auth=settings.WORLDMAP_ACCOUNT_AUTH,
                            timeout=settings.WORLDMAP_DEFAULT_TIMEOUT)
        except RequestsConnectionError as e:
            print 'err', e
            err_msg = 'Error connecting to WorldMap server: %s' % e.message
            LOGGER.error('Error trying to join to datatable with id: %s',\
                         self.datatable_obj.id)
            LOGGER.error(err_msg)
            self.add_error(err_msg)
            return False
        except:
            err_msg = "Unexpected error: %s" % sys.exc_info()[0]
            LOGGER.error(err_msg)
            self.add_error(err_msg)
            return False

        try:
            rjson = r.json()
        except:
            self.add_error("Sorry!  The mapping failed.  (%s)" % r.text)
            return False
        msg('rjson: %s' % json.dumps(rjson, indent=4))

        if rjson.get('success', False) is True:
            self.rjson_output = rjson
            # (True, (message, data))
            return True
        else:
            self.add_error(rjson.get('message', '(no message sent)'))
            return False
