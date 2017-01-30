import logging
from gc_apps.layer_types.static_vals import TYPE_SHAPEFILE_LAYER,\
                TYPE_JOIN_LAYER, TYPE_LAT_LNG_LAYER,\
                DV_MAP_TYPE_SHAPEFILE
from gc_apps.gis_tabular.models import WorldMapJoinLayerInfo, WorldMapLatLngInfo
from gc_apps.gis_shapefiles.models import WorldMapShapefileLayerInfo

LOGGER = logging.getLogger(__name__)

def get_worldmap_info_object(data_source_type, info_md5):
    """
    Based on the type of data, return the appropriate
    object containing WorldMap data

    shapefile -> WorldMapLayerInfo
    tabular join -> WorldMapJoinLayerInfo
    tabular lat/lng -> WorldMapLatLngInfo
    """
    if data_source_type in [TYPE_SHAPEFILE_LAYER, DV_MAP_TYPE_SHAPEFILE]:
        WORLDMAP_INFO_CLASS = WorldMapShapefileLayerInfo

    elif data_source_type == TYPE_JOIN_LAYER:
        WORLDMAP_INFO_CLASS = WorldMapJoinLayerInfo

    elif data_source_type == TYPE_LAT_LNG_LAYER:
        WORLDMAP_INFO_CLASS = WorldMapLatLngInfo

    else:
        err_note = 'data_source_type not recognized: %s' % data_source_type
        #assert False, err_note
        LOGGER.error(err_note)
        return None

    try:
        return WORLDMAP_INFO_CLASS.objects.get(md5=info_md5)
    except WORLDMAP_INFO_CLASS.DoesNotExist:
        err_note = ('Sorry! The layer data could not be found '
                    'for md5 "%s". '
                    '(%s object not found)' % (info_md5, data_source_type))
        LOGGER.error(err_note)
        return None
