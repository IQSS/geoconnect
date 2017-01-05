"""
Static variables used within geoconnect
"""

# --------------------------------------
# Used for incoming Dataverse Files
#   Note: The value types: 'shapefile', 'tabular', etc are in the
#         info returned by the Dataverse API
# --------------------------------------
DV_MAP_TYPE_SHAPEFILE = 'shapefile'
DV_MAP_TYPE_TABULAR = 'tabular'
DV_MAP_TYPE_GEOTIFF = 'geotiff'

DV_FILE_TYPES = (DV_MAP_TYPE_SHAPEFILE,\
                DV_MAP_TYPE_TABULAR,\
                DV_MAP_TYPE_GEOTIFF)
DV_FILE_TYPE_CHOICES = [(x, x) for x in DV_FILE_TYPES]

def is_valid_dv_type(map_type):
    return map_type in DV_FILE_TYPES

def is_dv_type_shapefile(map_type):
    return map_type == DV_MAP_TYPE_SHAPEFILE

def is_dv_type_tabular(map_type):
    return map_type == DV_MAP_TYPE_TABULAR

def is_dv_type_geotiff(map_type):
    return map_type == DV_MAP_TYPE_GEOTIFF

# --------------------------------------
# Used for classify and delete forms
# --------------------------------------
TYPE_SHAPEFILE_LAYER = 'TYPE_SHAPEFILE_LAYER'
TYPE_JOIN_LAYER = 'TYPE_JOIN_LAYER'
TYPE_LAT_LNG_LAYER = 'TYPE_LAT_LNG_LAYER'

# Tuple of array types
LAYER_TYPES = (TYPE_SHAPEFILE_LAYER, TYPE_JOIN_LAYER, TYPE_LAT_LNG_LAYER)

# Array types for "choices" settings
LAYER_TYPE_CHOICES = [(x, x) for x in LAYER_TYPES]

def is_valid_layer_type(map_type):
    return map_type in LAYER_TYPES

#from apps.layer_types.static_vals import
