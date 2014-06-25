#from __future__ import print_function
import sys
import pandas as pd

fname = '../test_data/tabular/meth_labs-01.xls'
df = pd.read_excel(fname, 0, index_col=None, na_values=['NA'])

#print(df.describe)
print(df.columns)

lat_lng_pairs = df[['Latitude', 'Longitude']].values

#col = df['Latitude']
#print 'Mean: ', col.mean()
#print 'Min: ', col.min()
#print 'Max: ', col.max()
#sys.exit(0)
#-----------------------------------
from osgeo import ogr

# Create a geometry collection
geomcol =  ogr.Geometry(ogr.wkbGeometryCollection)

# Add a point
point = ogr.Geometry(ogr.wkbPoint)
for lat,lng in lat_lng_pairs:
    point.AddPoint(lng, lat)#-122.23, 47.09)
    geomcol.AddGeometry(point)

print geomcol.ExportToWkt()


#------------------------------

for i in range(0, geomcol.GetGeometryCount()):
    g = geomcol.GetGeometryRef(i)
    print "(%i). %s" %(i, g.ExportToWkt())

#------------------------------
import ogr
cnt = ogr.GetDriverCount()
formatsList = []  # Empty List

for i in range(cnt):
    driver = ogr.GetDriver(i)
    driverName = driver.GetName()
    if not driverName in formatsList:
        formatsList.append(driverName)

formatsList.sort() # Sorting the messy list of ogr drivers

for i in formatsList:
    print i


"""
for v in location_info:
    loc_lines = v.split('\n')
    lat, lng = loc_lines[-1].replace('(','').replace(')','').split(',')
    print lng
"""    