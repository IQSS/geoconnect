from django.db import models


KEY_UPDATES_TO_MATCH_DATAVERSE_API = { 'worldmap_username' : 'worldmapUsername'\
                                    , 'layer_name' : 'layerName'\
                                    , 'layer_link' : 'layerLink'\
                                    , 'embed_map_link' : 'embedMapLink'\
                                    , 'datafile_id': 'datafileID'\
                                    #, 'dv_session_token' : 'dvSessionToken'\
                                    }
DATAVERSE_REQUIRED_KEYS = KEY_UPDATES_TO_MATCH_DATAVERSE_API.values()