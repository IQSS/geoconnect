# ------------------------------
# Quick script to add insitutions and
# affiliate them with dataverse installations
#
# Only deletes redundant institutions to refresh their affiliation
# ------------------------------
import os, sys
from os.path import abspath, isdir, realpath, isfile

proj_paths = [abspath('../'), abspath('../geoconnect')]
sys.path += proj_paths

# ------------------------------
# This is so Django knows where to find stuff.
# ------------------------------
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geoconnect.settings.local")

from geo_utils.msg_util import *

from gc_apps.gis_tabular.models import WorldMapJoinLayerInfo
from gc_apps.gis_tabular.unmapped_row_util import UnmatchedRowHelper


def check_unmatched(layer_info_md5):
    msgt('check_unmatched')
    wm_info = WorldMapJoinLayerInfo.objects.get(md5=layer_info_md5)

    kwargs = dict(show_all_failed_rows=True)
    unmatched_row_helper = UnmatchedRowHelper(wm_info, **kwargs)

    if unmatched_row_helper.has_error:
        msg('ERROR: %s' % unmatched_row_helper.error_message)
        return

    msgt('bad rows as list')
    row_list = unmatched_row_helper.get_failed_rows_as_list()
    if unmatched_row_helper.has_error:
        msg('ERROR: %s' % unmatched_row_helper.error_message)
        return
    msg(row_list)


    row_list_csv = unmatched_row_helper.get_failed_rows_as_csv()
    if unmatched_row_helper.has_error:
        msg('ERROR: %s' % unmatched_row_helper.error_message)
        return
    msg(row_list_csv)

if __name__ == '__main__':

    tab_md5 = '1a77cebad8a249820f2c577392dae20a'

    check_unmatched(tab_md5)
