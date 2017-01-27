from random import randint
import random
import string
from os.path import basename

class DataverseTestInfo(object):
    """
    Return somewhat random dataverse info for testing
    """
    def __init__(self):

        self.info_dict = {
    "title": "Boston Neighborhood Boundaries",
    "abstract": "Boston Redevelopment Authority Districts.  View in Dataverse: http://localhost:8080/dataset.xhtml?id=62 ",
    "dv_user_email": "dvuser@harvard.edu",
    "shapefile_name": "Neighborhoods_BRA_1.tiff",

    "datafile_content_type" : "image/tiff",
    "datafile_create_datetime": "2014-09-30 10:00:54.544",
    "datafile_expected_md5_checksum": "e16c3b9999781343ad6dfa180f176d7c",
    "datafile_download_url": "http://localhost:8080/api/access/datafile/1205",
    "datafile_filesize": 1106432,
    "datafile_id": 120555,
    "datafile_label": "Neighborhoods_BRA_1.tiff",

    "dataset_id": 42,
     "dataset_name": "Boston Data",
     "dataset_semantic_version": "V3",
     "dataset_citation": "BARI, 2015, \"Demographics for 2009 American Community Survey\", http://hdl.handle.net/1902.1/15586, Harvard Dataverse, V3",
     "dataset_description": "Hullo!",
     "dataset_version_id": 62,

    "dataverse_id": 1,
    "dataverse_name": "Root",
    "dataverse_installation_name": "http://localhost:8000",
    "dataverse_description": "The test dataverse.",

    "dv_user_id": 1,
    "dv_user_email": "dvuser@harvard.edu",
    "dv_username": "BARI",
    "return_to_dataverse_url": "http://localhost:8080/dataset.xhtml?id=62"
}

    @staticmethod
    def get_dataverse_test_info_dict(name, filename):

        dataverse_test_info = DataverseTestInfo()
        dti = dataverse_test_info.info_dict
        dti['title'] = name
        dti['dataset_name'] = 'Dataset {0}'.format(name)

        dti['datafile_label'] = basename(filename)    # e.g. "Neighborhoods_BRA_1.tiff"

        dti['dataverse_id'] = randint(1, 100)
        dti['dataverse_name'] = 'Dataverse {0}'.format(name)
        dti['dataverse_description'] = 'Description for {0}'.format(dti['dataverse_name'])


        dti['dataset_id'] = randint(100, 1000)
        dti['dataset_name'] = 'Dataset {0}'.format(name)
        dti['dataset_description'] = 'Description for {0}'.format(dti['dataset_name'])

        dti['dataset_version_id'] = randint(1, 10)
        dti['dataset_semantic_version'] = 'V{0}'.format(dti['dataset_version_id'])

        dti['datafile_id'] = randint(10000, 90000)
        dti['datafile_download_url'] = "http://localhost:8080/api/access/datafile/{0}".format(dti['datafile_id'])

        chars = string.ascii_uppercase + string.digits
        dti['datafile_expected_md5_checksum'] = ''.join(random.choice(chars) for _ in range(32))

        return dti
