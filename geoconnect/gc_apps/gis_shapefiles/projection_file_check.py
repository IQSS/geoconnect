"""
Examine a projection file (.prj) from a shapefile set
    - Check if the geographic coordinate system may be visualized by WorldMap
"""

class ProjectFileCheck:
    
        

# From WorldMap:  https://github.com/cga-harvard/cga-worldmap/blob/master/src/GeoNodePy/geonode/maps/forms.py
SRS_CHOICES = (
    ('EPSG:4326', 'EPSG:4326 (WGS 84 Lat/Long)'),
    ('EPSG:900913', 'EPSG:900913 (Web Mercator)'),
)