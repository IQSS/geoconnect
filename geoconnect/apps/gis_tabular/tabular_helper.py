from os.path import isfile
import sys
import csv
import json

from apps.gis_tabular.models import GeoType, TabularFileInfo
from apps.gis_tabular.models import SimpleTabularTest   # for testing

import logging
logger = logging.getLogger(__name__)


NUM_PREVIEW_ROWS = 40

class TabFileStats(object):

    def __init__(self, fname, delim=',', tabular_info=None):
        assert isfile(fname), "TabFileStats.  File does not exist: %s" % fname

        self.fname = fname
        self.delimiter = b','    #delim
        self.tabular_info = tabular_info

        self.header_row = []
        self.num_rows = 0
        self.num_cols = 0
        self.preview_rows = []

        self.stats_collected = False

        self.collect_stats()
        self.update_tabular_info_object()

    @staticmethod
    def create_tab_stats_from_tabular_info(tabular_info):
        assert isinstance(tabular_info, TabularFileInfo) or isinstance(tabular_info, SimpleTabularTest)\
            , 'tabular_info must be a TabularFileInfo or SimpleTabularTest object'

        assert tabular_info.dv_file is not None, "tabular_info.file cannot be None"

        return TabFileStats(fname=tabular_info.dv_file.file.name\
                            , delim=tabular_info.delimiter\
                            , tabular_info=tabular_info
                            )

    def collect_stats(self):
        """
        Open the file: collect num_rows, num_cols and preview_row data
        """
        print 'self.delimiter', self.delimiter, len(self.delimiter)
        with open(self.fname, 'rU') as f:
            reader = csv.reader(f, delimiter=self.delimiter, skipinitialspace=True)
            self.header_row = next(reader)
            self.num_cols = len(self.header_row)

            try:
                for row in reader:
                    self.num_rows += 1
            except csv.Error as e:
                logger.error('Error reading file: %s\nLine: %d\nMessage: %s' \
                                % (filename, reader.line_num, e))

        self.stats_collected = True

    def update_tabular_info_object(self):
        """
        If one is specified update the tabular_info object.

        This is usually a TabularFileInfo or SimpleTabularTest object
        """
        if not self.tabular_info:
            return

        self.tabular_info.num_rows = self.num_rows
        self.tabular_info.num_columns = self.num_cols

        if hasattr(self.tabular_info, "add_column_names"):
            self.tabular_info.add_column_names(self.header_row)
        else:
            try:
                json_header = json.dumps(self.header_row)
                self.tabular_info.column_names = json_header
            except:
                sys.exit(0)
                logger.error("Failed to convert header row (column names) to JSON.\n%s" % sys.exc_info()[0])


        if hasattr(self.tabular_info, "save"):
            self.tabular_info.save()