import logging

from datetime import timedelta

from django.utils import timezone
from django.conf import settings

from shared_dataverse_information.map_layer_metadata.forms import WorldMapToGeoconnectMapLayerMetadataValidationForm

from gc_apps.gis_shapefiles.models import ShapefileInfo, WorldMapShapefileLayerInfo

from gc_apps.gis_basic_file.dataverse_info_service import get_dataverse_info_dict

from gc_apps.worldmap_connect.worldmap_importer import WorldMapImporter
from gc_apps.worldmap_connect.dataverse_layer_services import get_layer_info_using_dv_info
from shared_dataverse_information.shapefile_import.forms import ShapefileImportDataForm

from gc_apps.dv_notify.metadata_updater import MetadataUpdater

LOGGER = logging.getLogger(__name__)

class SendShapefileService:
    """
    Logic for sending a shapefile to the WorldMap and processing the results
    """

    def __init__(self, **kwargs):
        """
        Constructor: send a ShapefileInfo object, or a ShapefileInfo object md5 attribute

        :param: shp_md5: str corresponding to a ShapefileInfo object
        :param shapefile_info: ShapefileInfo object
        """
        self.shapefile_info = None
        self.has_err = False
        self.err_msgs = []
        self.worldmap_response = None       # dict returned from WorldMapImporter or None
        self.worldmap_layerinfo = None      # WorldMapShapefileLayerInfo or None

        if kwargs.has_key('shapefile_info'):
            self.shapefile_info = kwargs['shapefile_info']
            assert isinstance(self.shapefile_info, ShapefileInfo),\
                    "shapefile_info must be a ShapefileInfo object"
        elif kwargs.has_key('shp_md5'):
            self.shapefile_info = self.load_shapefile_from_md5(kwargs['shp_md5'])
        else:
            LOGGER.debug('SendShapefileService Constructor. shapefile_info or shp_md5 is required')
            raise Exception('shapefile. shapefile_info or shp_md5 is required.')


    #def check_for_existing_map(self):

    def flow1_does_map_already_exist(self):
        """Check for an existing map in the Geoconnect database
        and on the WorldMap server"""

        # (1) Does the self.shapefile_info have what it needs?  Mainly a legit zippped shapefile
        #
        if not self.verify_shapefile():
            return False

        # (2) Check if a successful import already exists (WorldMapLayerInfo)
        if self.does_successful_import_already_exist():
            return True

        # (3) Check the WorldMap for an existing map layer
        if self.check_worldmap_for_existing_layer():
            return True

        return False

    def send_shapefile_to_worldmap(self):
        """
        TO DO : Option to make this happen via async.

        Main function that attempts to send a shapefile to WorldMap

        returns boolean indicating whether process worked
        """
        # (1) Does the self.shapefile_info have what it needs?  Mainly a legit zippped shapefile
        #
        if not self.verify_shapefile():
            return False

        # (2) Check if a successful import already exists (WorldMapLayerInfo), if it does, set the "self.worldmap_layerinfo"
        if self.does_successful_import_already_exist():
            return True

        # (3) Check the WorldMap for an existing map layer
        if self.check_worldmap_for_existing_layer():
            return True

        # (4) Map the information!
        if not self.send_file_to_worldmap():
            return False

        # (5) Process the WorldMap response
        #
        if not self.process_worldmap_response():
            return False

        # (6) Update Dataverse with new WorldMap info
        #       If this fails, ie, Dataverse not available, keep going...
        self.update_dataverse_with_worldmap_info()

        return True


    def check_worldmap_for_existing_layer(self):
        """Check the WorldMap API for an existing layer created
        this Dataverse shapefile"""
        if self.has_err:
            return False

        # Seems redundant, but this method may be called directly
        #
        if not self.verify_shapefile():
            return False

        success, dict_or_err_msg = get_layer_info_using_dv_info(self.shapefile_info.__dict__)

        if not success:
            #   Not an error, a layer commonly doesn't exist in WorldMap--and
            #   never for first time mappinga
            return False

        layer_info = WorldMapShapefileLayerInfo.build_from_worldmap_json(\
                                self.shapefile_info,\
                                dict_or_err_msg)

        if layer_info is None:  # Should always work!
            self.add_err_msg("Failed to create Map Layer from WorldMap JSON")
            return False

        self.worldmap_layerinfo = layer_info

        return True


    def add_err_msg(self, msg):
        LOGGER.error(msg)
        self.has_err = True
        self.err_msgs.append(msg)

    def load_shapefile_from_md5(self, shp_md5):
        """Load a ShapefileInfo based on an md5 attribute.
         Set self.shapefile_info to the retrieved ShapefileInfo

        :param: shp_md5: str corresponding to a ShapefileInfo object
        :returns: boolean
        """
        if shp_md5 is None:
            self.add_err_msg('shp_md5 is None')
            return None

        try:
            return ShapefileInfo.objects.get(md5=shp_md5)
        except ShapefileInfo.DoesNotExist:
            self.add_err_msg('Sorry, the shapefile was not found')
            return None


    def verify_shapefile(self):
        """
        Does the file specified by ShapefileInfo "dv_file" exist?

        :returns: boolean
        """
        if self.has_err:
            return False

        LOGGER.debug('verify_shapefile')
        if not self.shapefile_info:
            self.add_err_msg('verify_shapefile: The shapefile set is None')
            return False

        if not self.shapefile_info.has_shapefile:
            self.add_err_msg('verify_shapefile: This .zip does not contain a valid shapefile')
            return False

        if not self.shapefile_info.is_dv_file_available():
            self.add_err_msg('verify_shapefile: The file itself is not available.')
            return False

        return True


    def does_successful_import_already_exist(self):
        """
        Has this layer already been imported by WorldMap?
        If yes, then set the self.worldmap_layerinfo and stop here.

        :returns: boolean.  If True then the self.worldmap_layerinfo has been set
        """
        if not self.shapefile_info:
            self.add_err_msg('does_successful_import_already_exist: The shapefile_info is None')
            return False

        # Look for a recent WorldMapShapefileLayerInfo in the database
        #
        time_threshold = timezone.now() - timedelta(seconds=settings.WORLDMAP_LAYER_EXPIRATION)
        params = dict(shapefile_info=self.shapefile_info,\
                    modified__lt=time_threshold)
        wm_info = WorldMapShapefileLayerInfo.objects.filter(**params).first()
        if wm_info is None:
            return False

        self.worldmap_layerinfo = wm_info
        return True



    def send_file_to_worldmap(self):
        """
        Let's send this file over!
        """
        if self.has_err:
            return False

        # Prepare the parameters
        layer_params = self.format_params_for_mapping()
        if layer_params is None:
            return False

        # Instantiate the WorldMapImporter object and attempt the import
        #
        wmi = WorldMapImporter()
        worldmap_response = wmi.send_shapefile_to_worldmap(\
                                layer_params,
                                self.shapefile_info.dv_file)
        #                        self.shapefile_info.get_dv_file_fullpath())

        if not worldmap_response:
            self.add_err_msg('send_file_to_worldmap: worldmap_response was None!')
            return False

        self.worldmap_response = worldmap_response

        return True


    def format_params_for_mapping(self):
        """
        Use the ShapefileImportDataForm to prepare parameters for the WorldMap import request.
        """
        if self.has_err:
            # existing error
            return None

        if self.shapefile_info is None:
            self.add_err_msg("shapefile_info cannot be None")
            return None

        #  (1) Add some basic params such as title and abstract
        #
        zipped_shapefile_name = self.shapefile_info.get_dv_file_basename()
        if not zipped_shapefile_name:
            self.add_err_msg('format_params_for_mapping: Shapefile basename was not found')
            return None

        initial_params = dict(gis_data_file=self.shapefile_info,
                     title=zipped_shapefile_name,
                     abstract=self.shapefile_info.get_abstract_for_worldmap(),
                     shapefile_name=zipped_shapefile_name
                    )

        initial_params.update(self.shapefile_info.__dict__)

        # (2) Validate/Clean the data via a django form
        #       e.g. extra params ignored
        #
        f = ShapefileImportDataForm(initial_params)
        if not f.is_valid():
            form_errs_as_text = format_errors_as_text(f)
            err_msg = ('These are incorrect correct params for the'
                    ' ShapefileImportDataForm: \n%s') % form_errs_as_text
            self.add_err_msg(err_msg)
            return None

        # (3) Add (again) the basic Dataverse info
        #   - This is working with an older form, ShapefileImportDataForm
        #
        cleaned_params = f.cleaned_data

        dataverse_info_dict = get_dataverse_info_dict(self.shapefile_info)
        if dataverse_info_dict is None:
            err_msg = ('Failed to format DataverseInfo params using'
                    ' the shapefile_info object')
            self.add_err_msg(err_msg)
            return None

        cleaned_params.update(dataverse_info_dict)

        #print ('return params: %s' % params_dict)
        # Return the parameters
        #
        return cleaned_params


    def get_worldmap_layerinfo(self):
        return self.worldmap_layerinfo


    def process_worldmap_response(self):
        """Examine the WorldMap response and process it"""
        LOGGER.debug(self.process_worldmap_response.__doc__)
        if self.has_err:
            return False


        if not type(self.worldmap_response) is dict:
            self.add_err_msg('process_worldmap_response: worldmap_response is None')
            return False

        # ------------------------------------------------------
        #  Sanity check: Was the import marked as successful?
        # ------------------------------------------------------
        import_success = self.worldmap_response.get('success', False)
        if not import_success:
            self.add_err_msg('Failed to create a map layer.')
            return False

        # ------------------------------------------------------
        #  Sanity check: Did the import response have data?
        # ------------------------------------------------------
        wm_data = self.worldmap_response.get('data', None)
        if wm_data is None:
            self.add_err_msg('WorldMap says success but no layer data found')
            return False

        LOGGER.debug('wm_data: %s' % wm_data)

        # ------------------------------------------------------
        # Use form from MapLayerMetadata object to check results
        # ------------------------------------------------------
        validation_form = WorldMapToGeoconnectMapLayerMetadataValidationForm(wm_data)
        if not validation_form.is_valid():
            err_msg = ('Validation of WorldMap response failed.'
                        '  Errors:\n%s') % validation_form.errors
            self.add_err_msg(err_msg)
            #print f.errors
            return False

        LOGGER.debug('\nData valid')

        # ------------------------------------------------------
        # Create and Save a new WorldMapShapefileLayerInfo object
        # ------------------------------------------------------
        build_args = (self.shapefile_info, self.worldmap_response)
        self.worldmap_layerinfo =\
            WorldMapShapefileLayerInfo.build_from_worldmap_json(*build_args)

        return True


    def update_dataverse_with_worldmap_info(self):
        """
        Send WorldMap JSON data back to the Dataverse
        """
        LOGGER.debug("update_dataverse_with_worldmap_info: %s" % self.worldmap_layerinfo  )
        if self.worldmap_layerinfo is None:
            LOGGER.warn("Attempted to send Worldmap info to Dataverse when 'worldmap_layerinfo_object' was None")
            return False


        try:
            MetadataUpdater.update_dataverse_with_metadata(self.worldmap_layerinfo)
        except:
            LOGGER.warn('Error.  Layer created and saved BUT update to dataverse failed')
            return False

        return True


"""
from shared_dataverse_information.shapefile_import.forms import ShapefileImportDataForm
from gc_apps.gis_shapefiles.models import ShapefileInfo
"""
