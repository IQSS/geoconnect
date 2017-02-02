from os.path import isfile
import sys
import csv
import json
import pandas as pd

from gc_apps.gis_tabular.models import TabularFileInfo
import unicodedata

import logging
logger = logging.getLogger(__name__)


"""
unicodedata.normalize('NFKD', title).encode('ascii','ignore')
"""

NUM_PREVIEW_ROWS = 5

class TabFileStats(object):

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

        self.collect_stats()
        self.update_tabular_info_object()


    def has_error(self):
        return self.error_found

    def add_error(self, m):
        """
        Save error message encountered in the process of
        collecting stats or updating the tabularFileInfo object
        """
        self.error_found = True
        self.error_message = m

    @staticmethod
    def create_tab_stats_from_tabular_info(tabular_info):
        assert isinstance(tabular_info, TabularFileInfo)\
            , 'tabular_info must be a TabularFileInfo object'

        assert tabular_info.dv_file is not None, "tabular_info.file cannot be None"

        #   tabular_info.dv_file.file.name\
        return TabFileStats(file_object=tabular_info.dv_file\
                            , delim=tabular_info.delimiter\
                            , tabular_info=tabular_info
                            )

    def collect_stats(self):
        global NUM_PREVIEW_ROWS
        """
        Open the file: collect num_rows, num_cols and preview_row data
        """
        #import ipdb; ipdb.set_trace()
        try:
            if self.file_object.file.__class__.__name__ == 'S3Boto3StorageFile':
                file_path = self.file_object.url
            else:
                file_path = self.file_object.file.name

            #type(self.file_object.file)
            #<class 'storages.backends.s3boto3.S3Boto3StorageFile'>
            df = pd.read_csv(file_path,
                             sep=self.delimiter)
        except pd.parser.CParserError as e:
            err_msg = ('Could not process the file. '
                        'At least one row had too many values. '
                        '(error: %s)' % e.message)
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
        if 'BG_ID_10' in  df.columns:
            df['BG_ID_10'] = df['BG_ID_10'].astype(str)

        return

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
        """
        try:
            json_header = json.dumps(self.column_names)
            self.tabular_info.column_names = json_header
        except:
            sys.exit(0)
            logger.error("Failed to convert header row (column names) to JSON.\n%s" % sys.exc_info()[0])
        """

        self.tabular_info.save()
