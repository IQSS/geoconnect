import logging
from datetime import datetime, timedelta

from django.conf import settings

from shared_dataverse_information.map_layer_metadata.forms import WorldMapToGeoconnectMapLayerMetadataValidationForm

from apps.gis_shapefiles.models import ShapefileInfo, WorldMapShapefileLayerInfo

from apps.gis_basic_file.dataverse_info_service import get_dataverse_info_dict

from apps.worldmap_connect.format_helper import get_params_for_worldmap_connect
from apps.worldmap_connect.models import WorldMapImportAttempt, WorldMapImportFail, WorldMapLayerInfo
from apps.worldmap_connect.worldmap_importer import WorldMapImporter
from apps.worldmap_connect.dataverse_layer_services import get_layer_info_using_dv_info
from shared_dataverse_information.shapefile_import.forms import ShapefileImportDataForm


from apps.dv_notify.metadata_updater import MetadataUpdater


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
        self.import_attempt_obj = None      # WorldMapImportAttempt or None
        self.worldmap_response = None       # dict returned from WorldMapImporter or None
        self.worldmap_layerinfo = None      # WorldMapLayerInfo or None
        self.import_failure_object = None   # WorldMapImportFail or None

        if kwargs.has_key('shapefile_info'):
            self.shapefile_info = kwargs['shapefile_info']
        elif kwargs.has_key('shp_md5'):
            self.shapefile_info = self.load_shapefile_from_md5(kwargs['shp_md5'])
        else:
            LOGGER.debug('SendShapefileService Constructor. shapefile_info or shp_md5 is required')
            raise Exception('shapefile. shapefile_info or shp_md5 is required.')

        assert isinstance(self.shapefile_info, ShapefileInfo), "shapefile_info must be a ShapefileInfo object"

    #def check_for_existing_map(self):

    def flow1_does_map_already_exist(self):
        """Check for an existing map in the Geoconnect database
        and on the WorldMap server"""

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
        if self.send_file_to_worldmap():
            return True

        # (5) Process the WorldMap response
        #
        if not self.process_worldmap_response():
            return False

        # (6) Update Dataverse with new WorldMap info
        if not self.update_dataverse_with_worldmap_info():
            return False

        return True
        #--------------------------------------------------------------------
        #--------------------------------------------------------------------
        # Original code below
        #--------------------------------------------------------------------
        # (1) Does the self.shapefile_info have what it needs?  Mainly a legit zippped shapefile
        #
        if not self.verify_shapefile():
            return False

        # (2) Check if a successful import already exists (WorldMapLayerInfo), if it does, set the "self.worldmap_layerinfo"
        if self.does_successful_import_already_exist():
            return True
        elif self.has_err:      # This may have produced an error
            return False


        #elif self.has_err:      # This may have produced an error
        #    return False

        # (3) Make a WorldMapImportAttempt object and set it to "self.import_attempt_obj"
        #
        if not self.make_import_attempt_object():
            return False


        # (4) Use the WorldMapImporter object to send the layer to the WorldMap server
        #
        if not self.send_file_to_worldmap():
            return False


        # (5) Process the WorldMap response
        #
        if not self.process_worldmap_response():
            return False


        # (6) Update Dataverse with new WorldMap info
        if not self.update_dataverse_with_worldmap_info():
            return False

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



    def workflow2_check_for_existing_worldmap_layer(self):
        """
        Assumption: A check has already been made for a WorldMapLayerInfo object

        Used upon first viewing a file, check if the Layer already exists
        in WorldMap and create the associated objects:
            - WorldMapImportAttempt
            - WorldMapLayerInfo

        Cleanup note: get rid of WorldMapImportAttempt and simplify
            storage to hold JSON/python dicts instead of splitting out al fields
        """
        # (1) Does the self.shapefile_info have what it needs?  Mainly a legit zipped shapefile
        #
        if not self.verify_shapefile():
            return False

        # (2) Make a WorldMapImportAttempt object and set it to "self.import_attempt_obj"
        #
        if not self.make_import_attempt_object():
            return False

        # (3) Check if a shapefile created Layer already exists
        #   - dict_or_err_msg - if not an err, is the JSON response from WorldMap
        #
        success, dict_or_err_msg = get_layer_info_using_dv_info(self.shapefile_info.__dict__)
        if not success:
            return False

        if not 'data' in dict_or_err_msg:
            return False

        # (4) Make an Import Success object
        #   - Use form from MapLayerMetadata object to check results
        #
        f = WorldMapToGeoconnectMapLayerMetadataValidationForm(dict_or_err_msg['data'])
        if not f.is_valid():
            self.record_worldmap_failure(self.worldmap_response, \
                'Validation of WorldMap response failed.  Errors:\n%s'\
                % f.errors)
            #print f.errors
            return False

        #  (5) Create and Save a new WorldMapLayerInfo object
        #
        self.worldmap_layerinfo = WorldMapLayerInfo(**f.cleaned_data)
        self.worldmap_layerinfo.import_attempt=self.import_attempt_obj
        self.worldmap_layerinfo.save()
        LOGGER.debug('WorldMapLayerInfo saved')

        self.import_attempt_obj.import_success = True
        self.import_attempt_obj.save()
        LOGGER.debug('AttemptObject updated')

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
        time_threshold = datetime.now() - timedelta(seconds=settings.WORLDMAP_LAYER_EXPIRATION)
        params = dict(shapefile_info=self.shapefile_info,\
                    modified__lt=time_threshold)
        wm_info = WorldMapShapefileLayerInfo.objects.filter(**params).first()
        if wm_info is None:
            return False

        self.worldmap_layerinfo = wm_info
        return True

        #--------------------------------------------------------------------
        #--------------------------------------------------------------------
        # Original code below
        #--------------------------------------------------------------------

        # Retrieve the lastest WorldMapImportAttempt, if it exists
        wm_attempt = WorldMapImportAttempt.get_latest_attempt(self.shapefile_info)
        if not wm_attempt:
            return False

        # Did the attempt succeed
        if wm_attempt.did_import_succeed():

            # Is the WorldMapLayerInfo object available?
            success_info = wm_attempt.get_success_info()
            if success_info is not None:
                # Yes, all set!
                self.worldmap_layerinfo = success_info
                return True

        # Nope, ok, let's do some work
        return False



    def make_import_attempt_object(self):
        """
        Attempt to make a n WorldMapImportAttempt object and set it to "self.import_attempt_obj"

        :returns: boolean.  If True then the self.import_attempt_obj has been set

        """
        if not self.shapefile_info:
            self.add_err_msg('make_import_attempt_object: The shapefile_info is None')
            return False

        zipped_shapefile_name = self.shapefile_info.get_dv_file_basename()
        if not zipped_shapefile_name:
            self.add_err_msg('make_import_attempt_object: Shapefile basename was not found')
            return False

        wm_attempt = WorldMapImportAttempt(gis_data_file=self.shapefile_info\
                                        , title=zipped_shapefile_name\
                                        #, abstract='[place holder abstract for %s]' % self.shapefile_info.name\
                                        , abstract=self.shapefile_info.get_abstract_for_worldmap()
                                        , shapefile_name=zipped_shapefile_name\
                                        )
        try:
            wm_attempt.save()
        except:
            self.add_err_msg('Save of WorldMapImportAttempt failed')
            return False

        self.import_attempt_obj = wm_attempt
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
        worldmap_response = wmi.send_shapefile_to_worldmap(layer_params, self.shapefile_info.get_dv_file_fullpath())

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
            self.add_err_msg('make_import_attempt_object: Shapefile basename was not found')
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

    def xsend_file_to_worldmap(self):
        """
        Let's send this file over!
        """
        LOGGER.debug('send_file_to_worldmap')
        if not self.shapefile_info:
            self.add_err_msg('send_file_to_worldmap: The shapefile_info is None')
            return False

        if not self.import_attempt_obj:
            self.add_err_msg('send_file_to_worldmap: WorldMapImportAttempt was not found')
            return False

        # Prepare the parameters
        layer_params = get_params_for_worldmap_connect(self.import_attempt_obj)

        LOGGER.debug('send_file_to_worldmap 3')

        # Instantiate the WorldMapImporter object and attempt the import
        #
        wmi = WorldMapImporter()
        worldmap_response = wmi.send_shapefile_to_worldmap(layer_params, self.shapefile_info.get_dv_file_fullpath())

        if not worldmap_response:
            self.add_err_msg('send_file_to_worldmap: worldmap_response was None!')
            return False

        self.worldmap_response = worldmap_response

        return True


    def record_worldmap_failure(self, worldmap_response, fail_msg=None):
        if not worldmap_response:
            self.add_err_msg('Import failed.  (Worldmap generated error message not found)')
            return

        if fail_msg is None:
            fail_msg = worldmap_response.get('message', 'Import failed  (WorldMap generated error mesasge not avaiable)')
        self.add_err_msg(fail_msg)

        self.import_failure_object = WorldMapImportFail(import_attempt=self.import_attempt_obj\
                                        , msg=fail_msg\
                                        , orig_response=worldmap_response\
                                    )
        self.import_failure_object.save()


    def get_worldmap_layerinfo(self):
        return self.worldmap_layerinfo


    def process_worldmap_response(self):
        """Examine the WorldMap response and process it"""
        LOGGER.debug(self.process_worldmap_response.__doc__)

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
        f = WorldMapToGeoconnectMapLayerMetadataValidationForm(wm_data)
        if not f.is_valid():
            err_msg = ('Validation of WorldMap response failed.'
                        '  Errors:\n%s') % f.errors
            self.add_err_msg(err_msg)
            #print f.errors
            return False

        LOGGER.debug('\nData valid')

        # ------------------------------------------------------
        # Create and Save a new WorldMapLayerInfo object
        # ------------------------------------------------------
        self.worldmap_layerinfo = WorldMapShapefileLayerInfo.build_from_worldmap_json(wm_data)
        #self.worldmap_layerinfo = WorldMapLayerInfo(**f.cleaned_data)
        #self.worldmap_layerinfo.import_attempt=self.import_attempt_obj
        self.worldmap_layerinfo.save()
        #LOGGER.debug('WorldMapLayerInfo saved')

        #self.import_attempt_obj.import_success = True
        #self.import_attempt_obj.save()
        #LOGGER.debug('AttemptObject updated')

        return True


    def xprocess_worldmap_response(self):
        LOGGER.debug('process_worldmap_response')

        if not type(self.worldmap_response) is dict:
            self.add_err_msg('process_worldmap_response: worldmap_response is None')
            return False

        # ------------------------------------------------------
        #  Sanity check: Was the import marked as successful?
        # ------------------------------------------------------
        import_success = self.worldmap_response.get('success', False)
        if not import_success:
            self.record_worldmap_failure(self.worldmap_response)
            return False

        # ------------------------------------------------------
        #  Sanity check: Did the import response have data?
        # ------------------------------------------------------
        wm_data = self.worldmap_response.get('data', None)
        if wm_data is None:
            self.record_worldmap_failure(self.worldmap_response, 'WorldMap says success but no layer data found')
            return False

        LOGGER.debug('wm_data: %s' % wm_data)

        # ------------------------------------------------------
        # Use form from MapLayerMetadata object to check results
        # ------------------------------------------------------
        f = WorldMapToGeoconnectMapLayerMetadataValidationForm(wm_data)
        if not f.is_valid():
            self.record_worldmap_failure(self.worldmap_response, 'Validation of WorldMap response failed.  Errors:\n%s' % f.errors)
            #print f.errors
            return False

        LOGGER.debug('\nData valid')

        # ------------------------------------------------------
        # Create and Save a new WorldMapLayerInfo object
        # ------------------------------------------------------
        self.worldmap_layerinfo = WorldMapLayerInfo(**f.cleaned_data)
        self.worldmap_layerinfo.import_attempt=self.import_attempt_obj
        self.worldmap_layerinfo.save()
        LOGGER.debug('WorldMapLayerInfo saved')

        self.import_attempt_obj.import_success = True
        self.import_attempt_obj.save()
        LOGGER.debug('AttemptObject updated')

        return True


    def update_dataverse_with_worldmap_info(self):
        """
        Send WorldMap JSON data back to the Dataverse
        """
        LOGGER.debug("update_dataverse_with_worldmap_info: %s" % self.worldmap_layerinfo  )
        if self.worldmap_layerinfo is None:
            LOGGER.warn("Attempted to send Worldmap info to Dataverse when 'worldmap_layerinfo_object' was None")
            return False

        #assert isinstance(self.worldmap_layerinfo, WorldMapLayerInfo), \
        #    "self.worldmap_layerinfo must be a WorldMapLayerInfo object.  Found: %s" % #self.worldmap_layerinfo.__class__.__name__

        try:
            MetadataUpdater.update_dataverse_with_metadata(self.worldmap_layerinfo)
        except:
            self.record_worldmap_failure(self.worldmap_response, 'Error.  Layer created and saved BUT update to dataverse failed')
            return False

        return True


"""
from shared_dataverse_information.shapefile_import.forms import ShapefileImportDataForm
from apps.gis_shapefiles.models import ShapefileInfo
"""
