##  Incoming file from Dataverse

## Create mock lat/lng object

```python

python manage.py shell
from apps.gis_tabular.dataverse_test_info import DataverseTestInfo
from apps.gis_tabular.models import TabularFileInfo, WorldMapLatLngInfo, DEFAULT_TABULAR_DELIMITER
from apps.gis_tabular.forms import TabularFileInfoForm
from apps.registered_dataverse.models import RegisteredDataverse

# Create a new TabularFileInfo object

name = 'Zip code test (happiness)'
dv_file_path = 'happiness.tab'

dv_meta = DataverseTestInfo.get_dataverse_test_info_dict(\
                name,\
                dv_file_path)

# Add a RegisteredDataverse id, delimiter, and 0 counts
#
dv_meta['name'] = name
dv_meta['registered_dataverse'] = RegisteredDataverse.objects.first().id
dv_meta['delimiter'] = DEFAULT_TABULAR_DELIMITER
dv_meta['num_rows'] = 0
dv_meta['num_columns'] = 0

f = TabularFileInfoForm(dv_meta)
f.is_valid()
f.errors

tab_info = TabularFileInfo(**f.cleaned_data)
tab_info.save()

import pandas as pd
df = pd.read_csv('CBG Annual and Longitudinal Measures.xlsx')
df = pd.read_excel('CBG Annual and Longitudinal Measures.xlsx')
df.to_csv('CBG Annual and Longitudinal Measures.tab', '\t')
```



INSERT INTO maplayermetadata (id, isjoinlayer, joindescription, embedmaplink, layerlink, layername, mapimagelink, worldmapusername, dataset_id, datafile_id)      VALUES (DEFAULT, true, 'This file was joined with WorldMap layer x, y, z',     'https://worldmap.harvard.edu/maps/embed/?layer=geonode:zip_codes_2015_zip_s9i','https://worldmap.harvard.edu/data/geonode:zip_codes_2015_zip_s9i',     'geonode:zip_codes_2015_zip_s9i',     'http://worldmap.harvard.edu/download/wms/27289/png?layers=geonode%3Azip_codes_2015_zip_s9i&width=865&bbox=-71.1911091251%2C42.2270382738%2C-70.9228275369%2C42.3976144794&service=WMS&format=image%2Fpng&srs=EPSG%3A4326&request=GetMap&height=550',     'admin',1226,1235);    
