
from gis_shapefiles.models import ShapefileSet
from worldmap_import.models import WorldMapImportAttempt, WorldMapImportFail, WorldMapImportSuccess
from worldmap_import.worldmap_importer import WorldMapImporter

from django.conf import settings

logger = logging.getLogger(__name__)

class SendShapefileService:
    """
    Logic for sending a shapefile to the WorldMap and processing the results
    """
    
    def __init__(self, **kwargs):
        """
        Constructor: send a ShapefileSet object, or a ShapefileSet object md5 attribute

        :param: shp_md5: str corresponding to a ShapefileSet object 
        :param shapefile_set: ShapefileSet object
        """
        self.shapefile_set = None
        self.has_err = False
        self.err_msgs = []
        self.import_attempt_obj = None      # WorldMapImportAttempt or None
        self.worldmap_response = None       
        self.import_success_obj = None      # WorldMapImportSuccess or None
        
        if kwargs.has_key('shapefile_set'):
            self.shapefile_set = kwargs['shapefile_set']
        elif kwargs.has_key('shp_md5'):
            self.shapefile_set = self.load_shapefile_from_md5(kwargs['shp_md5'])
        else:
            logger.debug('SendShapefileService Constructor. shapefile_set or shp_md5 is required')
            raise Exception('shapefile. shapefile_set or shp_md5 is required.')    

    def send_shapefile_to_worldmap(self):
        """
        TO DO : Option to make this happen via async.
        
        Main function that attempts to send a shapefile to WorldMap
        
        :returns: boolean indicating whether process worked
        """
        
        # (1) Does the self.shapefile_set have what it needs?  Mainly a legit zippped shapefile
        #
        if not self.verify_shapefile():
            return False
            
        # (2) Check if a successful import already exists (WorldMapImportSuccess), if it does, set the "self.import_success_obj"
        #
        if self.does_successful_import_already_exist():
            return True
        elif self.has_err:      # This may have produced an error
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
        
        #return True
            
            
    def add_err_msg(self, msg):
        self.has_err = True
        self.err_msgs.append(msg)
    
    
    
    def load_shapefile_from_md5(self, shp_md5):
        """Load a ShapefileSet based on an md5 attribute.
         Set self.shapefile_set to the retrieved ShapefileSet 
        
        :param: shp_md5: str corresponding to a ShapefileSet object 
        :returns: boolean 
        """
        if shp_md5 is None:
            self.add_err_msg('shp_md5 is None')
            return False
            
        try:
            self.shapefile_set = ShapefileSet.objects.get(md5=shp_md5)
            return True
        except ShapefileSet.DoesNotExist:
            self.add_err_msg('Sorry, the shapefile was not found')
            return False
    
    
    def verify_shapefile(self):
        """
        Does the file specified by ShapefileSet "dv_file" exist?
        
        :returns: boolean 
        """
        if not self.shapefile_set:
            self.add_err_msg('verify_shapefile: The shapefile set is None')
            return False
        
        
        if not self.shapefile_set.has_shapefile:
            self.add_err_msg('verify_shapefile: This .zip does not contain a valid shapefile')
            return False

        if not self.shapefile_set.is_dv_file_available():
            self.add_err_msg('verify_shapefile: The file itself is not available.')
            return False
        
        return True
        
    
    def does_successful_import_already_exist(self):
        """
        Has this layer already been imported by WorldMap? 
        If yes, then set the self.import_success_obj and stop here.
        
        :returns: boolean.  If True then the self.import_success_obj has been set
        """
        if not self.shapefile_set:
            self.add_err_msg('does_successful_import_already_exist: The shapefile_set is None')
            return False
            
        # Retrieve the lastest WorldMapImportAttempt, if it exists
        wm_attempt = WorldMapImportAttempt.get_latest_attempt(self.shapefile_set)
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
        if not self.shapefile_set:
            self.add_err_msg('make_import_attempt_object: The shapefile_set is None')
            return False

        zipped_shapefile_name = self.shapefile_set.get_dv_file_basename()
        if not zipped_shapefile_name:
            self.add_err_msg('make_import_attempt_object: Shapefile basename was not found')
            return False
            
        wm_attempt = WorldMapImportAttempt(gis_data_file=self.shapefile_set\
                                        , title=zipped_shapefile_name\
                                        , abstract='[place holder abstract for %s]' % shapefile_set.name\
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
        if not self.shapefile_set:
            self.add_err_msg('send_file_to_worldmap: The shapefile_set is None')
            return False
        
        if not self.import_attempt_obj:
            self.add_err_msg('send_file_to_worldmap: WorldMapImportAttempt was not found')
            return False
        
        # Prepare the parameters
        layer_params = self.import_attempt_obj.get_params_for_worldmap_import(geoconnect_token=settings.WORLDMAP_TOKEN_FOR_DV)

        # Instantiate the WorldMapImporter object and attempt the import
        #
        wmi = WorldMapImporter(settings.WORLDMAP_SERVER_URL)
        worldmap_response = wmi.send_shapefile_to_worldmap(layer_params, self.shapefile_set.get_dv_file_fullpath())
        
        if not worldmap_response:
            self.add_err_msg('send_file_to_worldmap: worldmap_response was None!')
            return False
        
        self.worldmap_response = worldmap_response
        
        return True
        
    def process_worldmap_response(self):
        if not self.worldmap_response:
            self.add_err_msg('process_worldmap_response: worldmap_response is None')
            return False
        
        
        
        
        
        
        