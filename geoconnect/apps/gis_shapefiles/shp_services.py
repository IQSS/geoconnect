"""
- Using Dataverse information, create a ShapefileInfo information.
- Given a ShapefileInfo object, check for and
    return a WorldMapLayerInfo object, if available
"""
import json
import urllib2

from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

from shared_dataverse_information.dataverse_info.forms import DataverseInfoValidationForm
from apps.registered_dataverse.registered_dataverse_helper import find_registered_dataverse

from geo_utils.msg_util import msg, msgt
from geo_utils.error_result_msg import ErrResultMsg,\
    FAILED_NOT_A_REGISTERED_DATAVERSE

from apps.gis_shapefiles.models import ShapefileInfo
from apps.worldmap_connect.models import WorldMapImportAttempt, WorldMapLayerInfo
from apps.worldmap_connect.send_shapefile_service import SendShapefileService

import logging
LOGGER = logging.getLogger(__name__)


def add_worldmap_layerinfo_if_exists(shapefile_info):
    """
    Does the WorldMap already have a layer for this Dataverse DataFile?

    Check the WorldMap API.  If a layer exists, for this "shapefile_info",
    create the following:
        - WorldMapImportAttempt
        - WorldMapLayerInfo

    Expects shapefile_info to have these fields:
        - dataverse_installation_name
        - datafile_id
    """
    if shapefile_info is None:
        return False

    send_shp_service = SendShapefileService(**dict(shapefile_info=shapefile_info))

    success = send_shp_service.workflow2_check_for_existing_worldmap_layer()

    return success


def get_shapefile_from_dv_api_info(dv_session_token, dv_info_dict):
    """Using Dataverse API information, create a "ShapefileInfo" object.
    This function should only result in successful responses.

    return True/False, shp_md5 or ErrResultMsg

    Examples:  True, md5 from ShapefileInfo
               False,  ErrResultMsg

    To do: Make this into a separate class
    """
    assert dv_session_token is not None, "dv_session_token cannot be None"
    assert type(dv_info_dict) is dict, "dv_info_dict must be type 'dict'"


    #------------------------------
    # (1) Validate the data (DataverseInfoValidationForm)
    #------------------------------
    validation_form = DataverseInfoValidationForm(dv_info_dict)
    if not validation_form.is_valid():
        errs = [ '%s: %s' % (k, v) for k,v in validation_form.errors.items()]
        print (errs)
        form_errs = '\n'.join(errs)
        return False, ErrResultMsg(None, form_errs)


    #-------------------------------------------------
    # (2) Check if this is a Registered Dataverse
    #-------------------------------------------------
    registered_dataverse = find_registered_dataverse(dv_info_dict['return_to_dataverse_url'])
    if registered_dataverse is None:
        return False, ErrResultMsg(FAILED_NOT_A_REGISTERED_DATAVERSE\
                        , "This dataverse url was not recognized: %s" % dv_info_dict['return_to_dataverse_url']\
                    )

    #-------------------------------------------------
    # (3) Look for existing ShapefileInfo objects in the database
    #    ShapefileInfo objects are routinely deleted, but if file is already here, use it
    #       * todo: check for staleness, if the data is old delete it
    #-------------------------------------------------
    params_for_existing_check = dict(datafile_id=dv_info_dict.get('datafile_id', -1),\
        dataverse_installation_name=dv_info_dict.get('dataverse_installation_name', -1),\
        )

    existing_sets = ShapefileInfo.objects.filter(**params_for_existing_check\
                                ).values_list('id', flat=True\
                                ).order_by('created')

    existing_shapefile_info_ids = list(existing_sets)
    msgt('existing_shapefile_info_ids: %s' % existing_shapefile_info_ids)

    #-------------------------------------------------
    # add dv_session_token and registered_dataverse to dv_info_dict
    #-------------------------------------------------
    dv_info_dict['dv_session_token'] = dv_session_token
    dv_info_dict['registered_dataverse'] = registered_dataverse

    #------------------------------
    # (4) Existing ShapefileInfo(s) found:
    #  (a) Update the ShapefileInfo object
    #  (b) Delete other ShapefileInfo objects for this datafile and user
    #  (c) Return the md5
    #------------------------------
    if len(existing_shapefile_info_ids) > 1:

        # pop the last ShapefileInfo id off the list of existing_shapefile_info_ids
        shp_id = existing_shapefile_info_ids.pop()

        # delete the rest
        if len(existing_sets) > 0:
            ShapefileInfo.objects.filter(id__in=existing_shapefile_info_ids).delete()   # delete older ShapefileInfo(s)


    #------------------------------
    # (5) Get or create a new ShapefileInfo object
    #------------------------------
    msgt('(5) Get or create a new ShapefileInfo object')
    try:
        # Existing ShapefileInfo:
        #   (1) Assume file is already saved
        #   (2) update the data
        #
        shapefile_info = ShapefileInfo.objects.get(**params_for_existing_check)

        for key, value in dv_info_dict.iteritems():
            setattr(shapefile_info, key, value)

        # Save
        shapefile_info.save()
        msg('shapefile info saved')

        # If the file is still available, return it
        if shapefile_info.is_dv_file_available():
            return True, shapefile_info.md5
        else:
            # But the file isn't there!!  Delete ShapefileInfo and make a new one
            shapefile_info.delete()

    except ShapefileInfo.DoesNotExist:
        pass
    #except:
    #    msg('Failed to retrieve an existing ShapefileInfo object -- so create a new one')
    #    #return False, ErrResultMsg(None, 'Failed to retrieve an existing ShapefileInfo object')

    msg('new file')

    #------------------------------
    # New shapefile info, create object and attach file
    #------------------------------

    shapefile_info = ShapefileInfo(**dv_info_dict)
    shapefile_info.save()

    #------------------------------
    # Download and attach file
    #------------------------------
    datafile_download_url = dv_info_dict.get('datafile_download_url', '')

    # Add session token.  Gives permission to download/retrieve the file
    #   - http://localhost:8080/api/access/datafile/FILEID?key=YOURAPIKEY
    #
    datafile_download_url = '%s?key=%s' % (datafile_download_url, dv_session_token)
    msg('datafile_download_url: %s' % datafile_download_url)
    datafile_filename = dv_info_dict.get('datafile_label', '')

    tmp_shapefile = NamedTemporaryFile(delete=True)

    try:
        tmp_shapefile.write(urllib2.urlopen(datafile_download_url).read())
    except urllib2.HTTPError as e:
        shapefile_info.delete() # clear shapefile
        err_msg = 'Failed to download shapefile. HTTPError: %s \n\nurl: %s' % (str(e), datafile_download_url)
        return False, ErrResultMsg(None, err_msg)

    tmp_shapefile.flush()

    shapefile_info.dv_file.save(datafile_filename, File(tmp_shapefile))
    shapefile_info.save()

    return True, shapefile_info.md5
