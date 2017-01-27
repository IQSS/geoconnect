"""
This may be stop gap.
For rows that fail to map, the WorldMap only sends back the values
of the keys that failed to map.

- Was there a transform?
-
"""
import pandas as pd


from gc_apps.gis_tabular.models import WorldMapJoinLayerInfo

from geo_utils.tabular_util import get_orig_column_name,\
        get_worldmap_colname_format,\
        is_pandas_dtype_numeric
from geo_utils.msg_util import msgt, msg


MAX_FAILED_ROWS_TO_BUILD = 1000
MAX_FAILED_ROWS_TO_DISPLAY = 20

class UnmatchedRowHelper(object):
    """
    Used to display failed rows (limited number) as well as
    create a .csv file of failed rows
    """
    def __init__(self, worldmap_info, **kwargs):
        assert isinstance(worldmap_info, WorldMapJoinLayerInfo),\
            "worldmap_info must be a WorldMapJoinLayerInfo object"

        self.show_all_failed_rows = kwargs.get('show_all_failed_rows', False )
        self.max_failed_rows_to_build = kwargs.get('max_failed_rows_to_build', MAX_FAILED_ROWS_TO_BUILD)
        self.max_failed_rows_to_display = kwargs.get('max_failed_rows_to_display', MAX_FAILED_ROWS_TO_DISPLAY)
        self.include_header_row = kwargs.get('include_header_row', True)

        self.worldmap_info = worldmap_info

        self.has_unmatched_rows = False
        self.total_row_count = 0

        # potentially updated attrs
        self.unmatched_rows = []
        self.unmatched_record_values = None
        self.table_join_attribute = None
        self.was_formatted_column_created = False
        self.zero_pad_length = None

        # error checking
        self.has_error = False
        self.error_message = None

        # run the check
        self.run_check()

    def add_error_msg(self, err_msg):
        self.has_error = True
        self.error_message = err_msg

    def run_check(self):
        self.check_for_unmatched_rows()

    def get_failed_rows_as_list(self):
        assert self.has_unmatched_rows,\
            'Before calling this, check that "has_unmatched_rows" is True'

        if self.has_error:
            return None

        return self.build_failed_rows()

    def get_failed_rows_as_csv(self):
        assert self.has_unmatched_rows,\
            'Before calling this, check that "has_unmatched_rows" is True'

        if self.has_error:
            return None

        return self.build_failed_rows(as_csv=True)



    def check_for_unmatched_rows(self):

        # Are there any unmatched records?
        if self.worldmap_info.get_unmapped_record_count() < 1:
            return

        # Yup!
        self.has_unmatched_rows = True

        # Grab the values that failed to join
        #
        if self.worldmap_info.core_data and\
            'unmatched_records_list' in self.worldmap_info.core_data:
            self.unmatched_record_values = self.worldmap_info.core_data.get('unmatched_records_list', '')
            self.unmatched_record_values = self.unmatched_record_values.split(',')
        else:
            self.add_error_msg('unmatched record list not found')
            return

        # Get the join attribute
        #
        self.table_join_attribute = self.worldmap_info.core_data.get('table_join_attribute')
        if self.table_join_attribute is None:
            self.add_error_msg('table_join_attribute was None')
            return

        # Was a join column created?
        #
        self.was_formatted_column_created = self.worldmap_info.core_data.get('was_formatted_column_created', False)

        self.zero_pad_length = self.worldmap_info.core_data.get('zero_pad_length', None)
        if not (self.zero_pad_length and self.zero_pad_length > 0):
            self.zero_pad_length = None


    def build_failed_rows(self, as_csv=False):
        """
        Scenario 1: Filter rows in the original file matching the join column
                against the values list

        Scenario 2: New column was created (zero-padded, etc).  Add that new column
                    and then filter rows using that new column and the values list
        """
        if self.has_error:
            return None

        tabular_info = self.worldmap_info.tabular_info

        try:
            df = pd.read_csv(tabular_info.dv_file.path,\
                        sep=tabular_info.delimiter,\
                        )
        except pd.parser.CParserError as e:
            err_msg = ('Could not process the file. '
                        'At least one row had too many values. '
                        '(error: %s)' % e.message)
            self.add_error(err_msg)
            return None

        new_columns = [get_worldmap_colname_format(x) for x in df.columns]
        df.columns = new_columns

        # ------------------------------------------------------
        # No formatted column created! Filter values and return
        # ------------------------------------------------------

        if self.was_formatted_column_created is False and self.table_join_attribute in df.columns:


            if is_pandas_dtype_numeric(df[self.table_join_attribute].dtype):
                unmatched_vals = self.convert_values_to_numeric(self.unmatched_record_values)
            else:
                unmatched_vals = self.unmatched_record_values

            df_filtered = df.loc[df[self.table_join_attribute].isin(unmatched_vals)]
            self.total_row_count = len(df_filtered.index)

            if as_csv:
                df_filtered = df_filtered[:self.max_failed_rows_to_build]
                return df_filtered.to_csv(index=False, header=True)

            # Return the data as a list of lists
            #
            if self.max_failed_rows_to_display and self.max_failed_rows_to_display > 0:
                df_filtered = df_filtered[:self.max_failed_rows_to_display]

            return df_filtered.values.tolist()

        # ------------------------------------------------------
        # Hasty attempt, only working with zero padded items
        # ------------------------------------------------------
        if self.zero_pad_length is None:
            func_col_fmt = lambda x: '%s' % x
        else:
            zero_pad_fmt = '{0:0>%s}' % self.zero_pad_length
            func_col_fmt = lambda x: zero_pad_fmt.format(x)

        # ----------------------------------
        # make the column
        # ----------------------------------
        orig_column_name = get_orig_column_name(self.table_join_attribute)

        df[self.table_join_attribute] = df[orig_column_name].apply(\
                            lambda x: func_col_fmt(x))

        df2 = df.loc[df[self.table_join_attribute].isin(self.unmatched_record_values)]
        self.total_row_count = len(df2.index)

        # Return the data as a CSV file
        #
        if as_csv:
            df2 = df2[:self.max_failed_rows_to_build]

            return df2.to_csv(index=False, header=self.include_header_row)

        # Return the data as a list of lists
        #
        if self.max_failed_rows_to_display and self.max_failed_rows_to_display > 0:
            df2 = df2[:self.max_failed_rows_to_display]

        if self.include_header_row:
            return [df2.columns.tolist()] + df2.values.tolist()
        else:
            return df2.values.tolist()


    def convert_values_to_numeric(self, val_list):
        assert val_list is not None, 'val_list cannot be None'

        updated_list = []
        for val in val_list:
            if isinstance(val, (str, unicode)):
                try:
                    new_val = int(val)
                except ValueError:
                    new_val = float(val)
                updated_list.append(new_val)
            else:
                updated_list.append(val)
        return updated_list
