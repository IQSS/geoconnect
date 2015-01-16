


def view_delete_map(request):
    """
    Retrieve and view a :model:`gis_shapefiles.ShapefileInfo` object

    :shp_md5: unique md5 hash for a :model:`gis_shapefiles.ShapefileInfo`
    :template:`gis_shapefiles/view_02_single_shapefile.html`
    """
    logger.debug('-' * 40)
    logger.debug('view_delete_map')

    d = get_common_lookup(request)
    d['page_title'] = 'Delete Shapefile'
    d['WORLDMAP_SERVER_URL'] = settings.WORLDMAP_SERVER_URL
    d[GEOCONNECT_STEP_KEY] = STEP1_EXAMINE 

    if not request.POST:
        raise Http404('Page not found.')
        
        
    try:
        shapefile_info = ShapefileInfo.objects.get(md5=shp_md5)
        d['shapefile_info'] = shapefile_info
        
    except ShapefileInfo.DoesNotExist:
        logger.error('Shapefile not found for hash: %s' % shp_md5)
        raise Http404('Shapefile not found.')
    
    logger.debug('shapefile_info: %s' % shapefile_info)
