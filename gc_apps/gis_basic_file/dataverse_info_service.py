"""
See WorldMap model dataverse_info.models.DataverseInfo
    https://github.com/cga-harvard/cga-worldmap/blob/e8554beda280aefc02e0b75d10613272a4ca2786/src/GeoNodePy/geonode/dataverse_info/models.py

Translate the GISDataFile object into a dict that can be passed to the DataverseInfoValidationForm*
    * https://github.com/cga-harvard/cga-worldmap/blob/e8554beda280aefc02e0b75d10613272a4ca2786/src/GeoNodePy/geonode/dataverse_info/forms.py
"""
#from django.forms.models import model_to_dict
from gc_apps.gis_basic_file.models import GISDataFile
from shared_dataverse_information.dataverse_info.forms import DataverseInfoValidationForm


def get_dataverse_info_dict(gis_data_file):
    """
    Convert a GISDataFile or ShapefileInfo object into a dict containing only DataverseInfo attributes
    
    GISDataFile and ShapefileInfo should always pass the DataverseInfoValidationForm
    """
    assert isinstance(gis_data_file, GISDataFile), "gis_data_file must be a GISDataFile object. (Note: A ShapefileInfo is also a GISDataFile object)"

    f = DataverseInfoValidationForm(gis_data_file.__dict__)    
    
    if f.is_valid():
        return f.cleaned_data
    
    raise Exception('Dataverse Info is not valid')
    
"""
from gc_apps.gis_basic_file.dataverse_info_service import get_dataverse_info_dict
from gc_apps.gis_shapefiles.models import ShapefileInfo
s = ShapefileInfo.objects.all()[0]
"""