from os.path import isfile
import sys
import csv
import json
import pandas as pd

from apps.gis_tabular.models import TabularFileInfo
import unicodedata

import logging
logger = logging.getLogger(__name__)


"""
unicodedata.normalize('NFKD', title).encode('ascii','ignore')
"""

NUM_PREVIEW_ROWS = 100

class TabFileStats(object):

    def __init__(self, fname, delim=',', tabular_info=None):
        assert isfile(fname), "TabFileStats.  File does not exist: %s" % fname

        self.fname = fname

        self.delimiter = str(delim)
        print 'init delim:', self.delimiter, len(self.delimiter)
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

        return TabFileStats(fname=tabular_info.dv_file.file.name\
                            , delim=tabular_info.delimiter\
                            , tabular_info=tabular_info
                            )

    def collect_stats(self):
        global NUM_PREVIEW_ROWS
        """
        Open the file: collect num_rows, num_cols and preview_row data
        """
        print 'self.delimiter', self.delimiter, len(self.delimiter)

        try:
            df = pd.read_csv(self.fname,\
                        sep=self.delimiter,\
                        )
        except pd.parser.CParserError as e:
            err_msg = ('Could not process the file. '
                        'At least one row had too many values. '
                        '(error: %s)' % e.message)
            self.add_error(err_msg)
            return

        self.column_names = df.columns.values.tolist()
        self.num_cols = len(self.column_names)
        self.num_rows = len(df.index)

        self.preview_rows = df.head(NUM_PREVIEW_ROWS).values.tolist()

        if not self.preview_rows or len(self.preview_rows) == 0:
            self.add_error('No data rows in the file')
            return

        self.stats_collected = True


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
