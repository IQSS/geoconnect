import logging

from django.conf import settings

from apps.gis_shapefiles.models import ShapefileInfo

from apps.worldmap_connect.models import WorldMapImportAttempt, WorldMapImportFail, WorldMapImportSuccess
from apps.worldmap_connect.worldmap_importer import WorldMapImporter

from apps.dv_notify.metadata_updater import MetadataUpdater


logger = logging.getLogger(__name__)

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
        self.import_success_obj = None      # WorldMapImportSuccess or None
        self.import_failure_object = None   # WorldMapImportFail or None
        
        if kwargs.has_key('shapefile_info'):
            self.shapefile_info = kwargs['shapefile_info']
        elif kwargs.has_key('shp_md5'):
            self.shapefile_info = self.load_shapefile_from_md5(kwargs['shp_md5'])
        else:
            logger.debug('SendShapefileService Constructor. shapefile_info or shp_md5 is required')
            raise Exception('shapefile. shapefile_info or shp_md5 is required.')

        assert(type(self.shapefile_info), ShapefileInfo)
    
    def send_shapefile_to_worldmap(self):
        """
        TO DO : Option to make this happen via async.
        
        Main function that attempts to send a shapefile to WorldMap
        
        :returns: boolean indicating whether process worked
        """
        
        # (1) Does the self.shapefile_info have what it needs?  Mainly a legit zippped shapefile
        #
        if not self.verify_shapefile():
            return False
        
        # (2) Check if a successful import already exists (WorldMapImportSuccess), if it does, set the "self.import_success_obj"
        #
        if self.does_successful_import_already_exist():
            return True
        elif self.has_err:      # This may have produced an error
            print 'err!'
            return False
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
        
        return True
            
            
    def add_err_msg(self, msg):
        print (msg)
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
        If yes, then set the self.import_success_obj and stop here.
        
        :returns: boolean.  If True then the self.import_success_obj has been set
        """
        if not self.shapefile_info:
            self.add_err_msg('does_successful_import_already_exist: The shapefile_info is None')
            return False
            
        # Retrieve the lastest WorldMapImportAttempt, if it exists
        wm_attempt = WorldMapImportAttempt.get_latest_attempt(self.shapefile_info)
        if not wm_attempt:
            return False
            
        # Did the attempt succeed
        if wm_attempt.did_import_succeed():

            # Is the WorldMapImportSuccess object available?
            success_info = wm_attempt.get_success_info()
            if success_info is not None:
                # Yes, all set!
                self.import_success_obj = success_info
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
        if not self.shapefile_info:
            self.add_err_msg('send_file_to_worldmap: The shapefile_info is None')
            return False
        
        if not self.import_attempt_obj:
            self.add_err_msg('send_file_to_worldmap: WorldMapImportAttempt was not found')
            return False
        
        # Prepare the parameters
        layer_params = self.import_attempt_obj.get_params_for_worldmap_connect(geoconnect_token=settings.WORLDMAP_TOKEN_FOR_DATAVERSE)
        print('send_file_to_worldmap 3')

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
        
        
    def get_import_success_object(self):
        return self.import_success_obj


    def process_worldmap_response(self):
        if not type(self.worldmap_response) is dict:
            self.add_err_msg('process_worldmap_response: worldmap_response is None')
            return False

        #  Sanity check: Was the import marked as successful?
        #
        import_success = self.worldmap_response.get('success', False)
        if not import_success:
            self.record_worldmap_failure(self.worldmap_response)
            return False
        
        #  Sanity check: Did the import response have data?
        #
        wm_data = self.worldmap_response.get('data', None)
        if wm_data is None:
            self.record_worldmap_failure(self.worldmap_response, 'WorldMap says success but no layer data found')
            return False
        
        
        logger.debug('wm_data: %s' % wm_data)
        try:
            # Success!  Create a WorldMapImportSuccess object
            #
            self.import_success_obj = WorldMapImportSuccess(import_attempt=self.import_attempt_obj\
                                            , layer_name=wm_data.get('layer_name', '')\
                                            , layer_link=wm_data.get('layer_link', '')\
                                            , embed_map_link=wm_data.get('embed_map_link', '')\
                                            , worldmap_username=wm_data.get('worldmap_username', '')\
                                        )
            self.import_success_obj.add_attribute_info(wm_data.get('attribute_info', None))
            self.import_success_obj.save()
            logger.debug('--- SAVED ---')
            self.import_attempt_obj.import_success = True
            self.import_attempt_obj.save()

        except:
            # Fail! Something in the return data seems to be incorrect.  e.g., Missing parameter such as layer_link
            # Save a WorldMapImportFail object to check original response
            #
            logger.debug('--- Failed to save worldmap data\n%s ---' % wm_data)
            self.record_worldmap_failure(self.worldmap_response, 'WorldMap says success but GeoConnect failed to save results')
            return False

        # Separate this into another async. task!
        # Send message back to the Dataverse -- to update metadata
        #
        # Round-trip example, break into separate process with 
        #   MetadataUpdateFail, MetadataUpdateSuccess objects
        try:
            MetadataUpdater.update_dataverse_with_metadata(self.import_success_obj)
        except:
            self.record_worldmap_failure(self.worldmap_response, 'Error.  Layer created and saved BUT update to dataverse failed')
            return False
            
        return True




