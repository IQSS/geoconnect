from django.conf import settings

"""
URLs for APIS used to contact the WorldMap

"""

def format_worldmap_api_url(url_path):
    assert url_path is not None, "url path cannot be None"
    
    formatted_url = '/'.join(s for s in (settings.WORLDMAP_SERVER_URL.strip('/'), url_path.lstrip('/')))
    #print ('formatted_url: %s' % formatted_url)
    return formatted_url


# shapefile import API
#
ADD_SHAPEFILE_API_PATH = format_worldmap_api_url('/dataverse/import/')

# classify layer API
#
CLASSIFY_LAYER_API_PATH = format_worldmap_api_url('/dataverse/classify-layer/')


# Get existing layer by Dataverse user id and Dataverse file id
#
GET_LAYER_INFO_BY_USER_AND_FILE_API_PATH = format_worldmap_api_url('/dataverse-layer/get-existing-layer-info/')


# Get existing layers by Dataverse user id
#
GET_LAYER_INFO_BY_USER_API_PATH = format_worldmap_api_url('/dataverse-layer/get-dataverse-user-layers/')


#
#
GET_VIEW_PRIVATE_LAYER_URL = format_worldmap_api_url('dataverse-private-layer/request-private-layer-url/')
