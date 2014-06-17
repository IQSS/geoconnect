import folium

# New Haven
#map_nh = folium.Map(location=[41.28, -72.88])
map_nh.simple_marker([41.252661, -72.890195], popup='My Popup Message')
#map_nh.create_map(path='nh.html')

# Boston 
mboston = folium.Map(location=[ 42.3267154, -71.1512353])
mboston.geo_json('HOSPITALS.geojson')
#mboston.geo_json('income.json')
mboston.create_map(path='boston2.html')
print 'file written', 'boston2.html'

#map.geo_json(geo_path='my_geo.json')

#HOSPITALS.geojson