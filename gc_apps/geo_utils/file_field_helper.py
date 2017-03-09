"""
Convenience method for reading a Django FileField
that may link to an AWS object
    - e.g. When reading the file from pandas,
      use either the '.path' or the '.url '
"""
from django.db.models.fields.files import FieldFile

def get_file_path_or_url(dv_file):
    """
    Given a Django FieldFile Return the path or the url to the file

    If the dv_file doesn't have an associated file, return None
    """
    assert isinstance(dv_file, FieldFile),\
        "file_field must be a Django FileField"

    if not hasattr(dv_file, 'file'):
        return None

    try:
        return dv_file.path
    except NotImplementedError:
        pass

    try:
        return dv_file.url
    except NotImplementedError:
        pass

    raise Exception('dv_file has neither a ".path" or ".url" for access')


"""
from gc_apps.geo_utils.file_field_helper import get_file_path_or_url
from gc_apps.gis_tabular.models import WorldMapJoinLayerInfo
w = WorldMapJoinLayerInfo.objects.first()
get_file_path_or_url(w.tabular_info.dv_file)

from gc_apps.gis_tabular.models import TabularFileInfo
t = TabularFileInfo()
get_file_path_or_url(t.dv_file)

"""
