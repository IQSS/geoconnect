"""
Gather tabular file information: number of rows, column names, etc
"""
import pandas as pd
from django.core.files.base import ContentFile

from gc_apps.gis_tabular.models import TabularFileInfo
from gc_apps.geo_utils.file_field_helper import get_file_path_or_url
from gc_apps.geo_utils.tabular_util import normalize_colname

import logging
LOGGER = logging.getLogger(__name__)


NUM_PREVIEW_ROWS = 5

class TabFileStats(object):
    """Gather tabular file information: number of rows, column names, etc"""

    def __init__(self, file_object, delim=',', tabular_info=None):

        assert hasattr(file_object, 'read'),\
            "TabFileStats.  file_object does not have .read() function: %s" % file_object

        self.file_object = file_object

        self.delimiter = str(delim)
        #print 'init delim:', self.delimiter, len(self.delimiter)
        #'\t' #str(delim)  #b','    #delim
        self.tabular_info = tabular_info

        self.column_names = []
        self.num_rows = 0
        self.num_cols = 0
        self.preview_rows = []

        self.error_found = False
        self.error_message = None

        self.stats_collected = False

        self.rename_columns()
        self.collect_stats()
        self.update_tabular_info_object()


    def has_error(self):
        """Was there an error?"""
        return self.error_found

    def add_error(self, message):
        """
        Save error message encountered in the process of
        collecting stats or updating the tabularFileInfo object
        """
        self.error_found = True
        self.error_message = message

    @staticmethod
    def create_from_tabular_info(tabular_info):
        assert isinstance(tabular_info, TabularFileInfo)\
            , 'tabular_info must be a TabularFileInfo object'

        assert tabular_info.dv_file is not None, "tabular_info.file cannot be None"

        #   tabular_info.dv_file.file.name\
        return TabFileStats(file_object=tabular_info.dv_file,
                            delim=tabular_info.delimiter,
                            tabular_info=tabular_info)

    def rename_columns(self):
        if self.has_error():
            return
        try:
            df = pd.read_csv(get_file_path_or_url(self.file_object),
                             sep=self.delimiter)
        except pd.parser.CParserError as ex_obj:
            err_msg = ('Could not process the file. '
                       'At least one row had too many values. '
                       '(error: %s)') % ex_obj.message
            self.add_error(err_msg)
            return
        count = 0
        columns_renamed = {}
        for column in df.columns.values.tolist():
            #print column
            normalized = normalize_colname(colname=column, position=count + 1)
            #print "BEFORE:", column
            #print "AFTER: ", normalized
            if column != normalized:
                columns_renamed[column] = normalized
            count += 1
        # write the CSV/TSV back out with safe column names
        #print "columns changed:", columns_renamed
        if len(columns_renamed) > 0:
            df.rename(columns=columns_renamed, inplace=True)

            df.to_csv(get_file_path_or_url(self.file_object),
                               sep=self.delimiter,
                               index=False)

            # http://stackoverflow.com/questions/36519086/pandas-how-to-get-rid-of-unnamed-column-in-a-dataframe
            """
            fh_csv = df.to_csv(get_file_path_or_url(self.file_object),
                               sep=self.delimiter,
                               index=False)

            content_file = ContentFile(fh_csv)#df.to_csv(**csv_parms))

            # Save the ContentFile in the tabular_info object
            # ----------------------------------
            self.tabular_info.dv_file.save(self.tabular_info.datafile_label,
                                           content_file)
            """


    def collect_stats(self):
        """
        Open the file: collect num_rows, num_cols and preview_row data
        """
        if self.has_error():
            return
        try:
            df = pd.read_csv(get_file_path_or_url(self.file_object),
                             sep=self.delimiter)
        except pd.parser.CParserError as ex_obj:
            err_msg = ('Could not process the file. '
                       'At least one row had too many values. '
                       '(error: %s)') % ex_obj.message
            self.add_error(err_msg)
            return

        self.special_case_col_formatting(df)

        self.column_names = df.columns.values.tolist()
        self.num_cols = len(self.column_names)
        self.num_rows = len(df.index)

        self.preview_rows = df.head(NUM_PREVIEW_ROWS).values.tolist()

        if not self.preview_rows or len(self.preview_rows) == 0:
            self.add_error('No data rows in the file')
            return

        self.stats_collected = True


    def special_case_col_formatting(self, df):
        """Will eventually need to be factored out"""
        if df is None:
            return

        # Treat census block groups as string instead of numbers
        #   - 12-digit numeric code that may receive zero-padding
        #
        keep_as_string_cols = ['BG_ID_10', 'CT_ID_10']
        for col_name in keep_as_string_cols:
            if col_name in  df.columns:
                df[col_name] = df[col_name].astype(str)


    def update_tabular_info_object(self):
        """
        If one is specified update the tabular_info object.

        This is usually a TabularFileInfo object
        """
        if self.has_error():
            return

        if not self.tabular_info:
            return

        self.tabular_info.num_rows = self.num_rows
        self.tabular_info.num_columns = self.num_cols
        self.tabular_info.column_names = self.column_names


        self.tabular_info.save()
