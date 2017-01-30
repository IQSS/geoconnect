"""Given an md5 for ShapefileInfo object, determine what state of the ShapefileInfo

Assumption: Assume the data and file have already been retrieved from Dataverse

Determine:
    - Has the file been validated as a shapefile?
    - Does a visualization already exist in WorldMap?
        - If so, display the classify form
    etc.
"""
from django.conf import settings

from gc_apps.gis_shapefiles.forms import ShapefileInfoForm
from gc_apps.gis_shapefiles.models import ShapefileInfo, WORLDMAP_MANDATORY_IMPORT_EXTENSIONS
from gc_apps.gis_shapefiles.shapefile_zip_check import ShapefileZipCheck



class ShapefileExamineUtil(object):

    def __init__(self, shapefile_info, **kwargs):

        assert isinstance(shapefile_info, ShapefileInfo),\
            "shapefile_info must be an instance of ShapefileInfo"

        self.shapefile_info = shapefile_info

        # flags that may have come through the view
        self.first_time_notify = kwargs.get('first_time_notify', False)

        # for error messages
        self.has_err = False
        self.err_msg = None
        self.err_type = None

        self.run_examination()


    def add_err_msg(self, msg, err_type=None):
        """Add error message for use by view"""

        #LOGGER.error(msg)
        self.has_err = True
        self.err_msg = msg
        self.err_type = err_type

    def run_examination(self):
        if self.has_err:
            return False

        if not self.is_shapefile_checked():
            return False


    def is_shapefile_checked(self):
        return True
