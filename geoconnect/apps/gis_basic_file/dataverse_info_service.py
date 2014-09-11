"""
See WorldMap model dataverse_info.models.DataverseInfo
    https://github.com/cga-harvard/cga-worldmap/blob/e8554beda280aefc02e0b75d10613272a4ca2786/src/GeoNodePy/geonode/dataverse_info/models.py

Translate the GISDataFile object into a dict that can be passed to the DataverseInfoValidationForm*
    * https://github.com/cga-harvard/cga-worldmap/blob/e8554beda280aefc02e0b75d10613272a4ca2786/src/GeoNodePy/geonode/dataverse_info/forms.py
"""
from django.forms.models import model_to_dict
from apps.gis_basic_file.models import GISDataFile

def format_gisbasicfile_for_worldmap(gis_file_obj):
    if not type(GISDataFile):
        raise TypeError('gis_file_obj is not a GISDataFile')
        
    return model_to_dict(gis_file_obj)
"""
f = GISDataFile.objects.all()[0]
d = model_to_dict(f)
for k, v in d.items():
    print """   , %s='%s'""" % (k,v)
"""