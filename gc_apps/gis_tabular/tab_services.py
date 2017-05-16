"""
- Using Dataverse information, create a TabularFileInfo information.
- Given a TabularFileInfo object, check for and
    return a TabularFileInfo object, if available
"""
from __future__ import print_function

import urllib2

from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

from shared_dataverse_information.dataverse_info.forms import DataverseInfoValidationForm
from gc_apps.registered_dataverse.registered_dataverse_helper import find_registered_dataverse
from gc_apps.gis_tabular.models import TabularFileInfo
from gc_apps.gis_tabular.models import WorldMapTabularLayerInfo

from gc_apps.geo_utils.msg_util import msg, msgt
from gc_apps.geo_utils.error_result_msg import ErrResultMsg, FAILED_NOT_A_REGISTERED_DATAVERSE

from gc_apps.worldmap_connect.dataverse_layer_services import get_layer_info_using_dv_info


import logging
LOGGER = logging.getLogger(__name__)


def add_worldmap_layerinfo_if_exists(tabular_info):
    """
    Does the WorldMap already have a layer for this Dataverse DataFile?

    Check the WorldMap API.  If a layer exists, for this "tabular_info",
    create one of the following:
        - WorldMapLatLngInfo
        - WorldMapJoinLayerInfo

    Expects tabular_info to have these fields:
        - dataverse_installation_name
        - datafile_id
    """
    if tabular_info is None:
        return False

    success, dict_or_err_msg = get_layer_info_using_dv_info(tabular_info.__dict__)

    if not success:
        return False

    worldmap_tabular_info = WorldMapTabularLayerInfo.build_from_worldmap_json(\
                                tabular_info,\
                                dict_or_err_msg)

    if worldmap_tabular_info is None:
        LOGGER.error("Failed to create WorldMapTabularLayerInfo using %s",\
                    dict_or_err_msg)
        return False

    return True


    # Let's make this into an actual object...
    #if


"""
from gc_apps.gis_tabular.tab_services import check_if_already_mapped
d = dict(dataverse_installation_name='http://localhost:8000', datafile_id=7193)

d = dict(dataverse_installation_name='http://localhost:8000', datafile_id=15562)
check_if_already_mapped(d)
"""



def get_tabular_file_from_dv_api_info(dv_session_token, dataverse_info_dict):
    """Using Dataverse API information, create a :model:`gis_tabular.TabularFileInfo' object.
    This function should only return successful responses.

    return True/False, shp_md5 or ErrResultMsg

    Examples:  True, md5 from TabularFileInfo
               False,  ErrResultMsg
    """
    assert dv_session_token is not None, "dv_session_token cannot be None"
    assert type(dataverse_info_dict) is dict,\
        "dataverse_info_dict must be type 'dict'"

    msgt('dataverse_info_dict: {0}'.format(dataverse_info_dict))
    #------------------------------
    # (1) Validate the data (DataverseInfoValidationForm)
    #------------------------------
    #dataverse_info_dict.update({'datafile_id':None})   # for testing
    validation_form = DataverseInfoValidationForm(dataverse_info_dict)
    if not validation_form.is_valid():
        errs = ['%s: %s' % (k, v) for k,v in validation_form.errors.items()]
        LOGGER.debug('errors: %s', errs)
        form_errs = '\n'.join(errs)
        return False, ErrResultMsg(None, form_errs)


    #-------------------------------------------------
    # (2) Check if this is a Registered Dataverse
    #-------------------------------------------------
    registered_dataverse = find_registered_dataverse(dataverse_info_dict['return_to_dataverse_url'])
    if registered_dataverse is None:
        return False, ErrResultMsg(\
                    FAILED_NOT_A_REGISTERED_DATAVERSE,
                    "This dataverse url was not recognized: %s" %\
                    dataverse_info_dict['return_to_dataverse_url'])

    #-------------------------------------------------
    # (3b) Look for existing Dataverse files in the database
    #    ShapefileInfo and TabularFileInfo objects are routinely
    #    deleted, but if file is already here, use it
    #-------------------------------------------------
    params_for_existing_check = dict(datafile_id=dataverse_info_dict.get('datafile_id', -1)\
                                    , dataverse_installation_name=dataverse_info_dict.get('dataverse_installation_name', -1)\
                                    )

    existing_sets = TabularFileInfo.objects.filter(**params_for_existing_check\
                                ).values_list('id', flat=True\
                                ).order_by('created')

    existing_tabular_info_ids = list(existing_sets)
    msgt('existing_tabular_info_ids: %s' % existing_tabular_info_ids)

    #-------------------------------------------------
    # add dv_session_token and registered_dataverse to dataverse_info_dict
    #-------------------------------------------------
    dataverse_info_dict['dv_session_token'] = dv_session_token
    dataverse_info_dict['registered_dataverse'] = registered_dataverse

    #------------------------------
    # (4) Existing TabularFileInfo(s) found:
    #  (a) Update the TabularFileInfo object
    #  (b) Delete other groups TabularFileInfo object for this datafile and user
    #  (c) Return the md5
    #------------------------------
    if len(existing_tabular_info_ids) > 1:

        # pop the last TabularFileInfo id off the list of existing_tabular_info_ids
        shp_id = existing_tabular_info_ids.pop()

        # delete the rest
        if len(existing_sets) > 0:
            # delete older TabularFileInfo objects
            TabularFileInfo.objects.filter(id__in=existing_tabular_info_ids).delete()


    #------------------------------
    # (5) Get or create a new TabularFileInfo object
    #------------------------------
    msgt('(5) Get or create a new TabularFileInfo object')
    try:
        # Existing TabularFileInfo:
        #   (1) Assume file is already saved
        #   (2) update the data
        #
        tabular_info = TabularFileInfo.objects.get(**params_for_existing_check)

        for key, value in dataverse_info_dict.iteritems():
            if key == 'column_names':
                tabular_info.add_column_names(value)
            else:
                setattr(tabular_info, key, value)

        # Save
        tabular_info.save()
        msg('tabular_info info saved')

        # If the file is still available, return it
        if tabular_info.is_dv_file_available():
            add_worldmap_layerinfo_if_exists(tabular_info)
            return True, tabular_info.md5
        else:
            # But the file isn't there!!  Delete TabularFileInfo and make a new one
            tabular_info.delete()

    except TabularFileInfo.DoesNotExist:
        pass
    #except:
    #    msg('Failed to retrieve an existing ShapefileInfo object -- so create a new one')
    #    #return False, ErrResultMsg(None, 'Failed to retrieve an existing ShapefileInfo object')

    msg('new file')

    #------------------------------
    # New tabular_info, create object and attach file
    #------------------------------

    # Add name parameter
    dataverse_info_dict['name'] = dataverse_info_dict.get('datafile_label', '(no datafile_label found)')
    tabular_info = TabularFileInfo(**dataverse_info_dict)
    tabular_info.save()

    #------------------------------
    # Download and attach file
    #------------------------------
    datafile_download_url = dataverse_info_dict.get('datafile_download_url', '')

    # Add session token.  Gives permission to download/retrieve the file
    #   - http://localhost:8080/api/access/datafile/FILEID?key=YOURAPIKEY
    #
    datafile_download_url = '%s?key=%s' % (datafile_download_url, dv_session_token)
    msg('datafile_download_url: %s' % datafile_download_url)
    datafile_filename = dataverse_info_dict.get('datafile_label', '')

    img_temp = NamedTemporaryFile(delete=True)

    try:
        img_temp.write(urllib2.urlopen(datafile_download_url).read())
    except urllib2.HTTPError as e:
        tabular_info.delete() # clear tabular info
        err_msg = 'Failed to download tabular file. HTTPError: %s \n\nurl: %s' % (str(e), datafile_download_url)
        return False, ErrResultMsg(None, err_msg)
    img_temp.flush()

    tabular_info.dv_file.save(datafile_filename, File(img_temp))
    tabular_info.save()
    add_worldmap_layerinfo_if_exists(tabular_info)

    return True, tabular_info.md5
