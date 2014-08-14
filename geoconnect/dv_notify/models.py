from django.db import models
from django.conf import settings

KEY_UPDATES_TO_MATCH_DATAVERSE_API = { 'worldmap_username' : 'worldmapUsername'\
                                    , 'layer_name' : 'layerName'\
                                    , 'layer_link' : 'layerLink'\
                                    , 'embed_map_link' : 'embedMapLink'\
                                    , 'datafile_id': 'datafileID'\
                                    , 'dv_session_token' : settings.DATAVERSE_TOKEN_KEYNAME\
                                    }
DATAVERSE_REQUIRED_KEYS = KEY_UPDATES_TO_MATCH_DATAVERSE_API.values()