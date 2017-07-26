
This README contains additional information on the following:

  - [Maintenance mode](#maintenance-mode)
  - [Mappable File Types](#mappable-file-types)
  - [Colors for Layer Styling](#colors-for-layer-styling)
  - [WorldMap Join Targets](#worldmap-join-targets)
  - [Tabular Column Formatting](#tabular-column-formatting)

# Maintenance mode

Geoconnect may be placed in maintenance mode via the administrative interface.  This is useful when either Dataverse or WorldMap is not available or undergoing maintenance.

### Step 1: Go to the geoconnect administrative interface.
### Step 2: Click Maintenance Mode
![admin page 1](readme_imgs/maint_mode_01.png?raw=true "admin page 1")
### Step 3: Click Maintenance Mode (again!)
![admin page 2](readme_imgs/maint_mode_02.png?raw=true "admin page 2")
### Step 4: Turn Maintenance mode on
  1. Check "is active"
  1. Set the date/time when the maintenance mode will end
      - Note: This date/time is for display only.  Maintenance mode needs to be turned off manually by unchecking "is active"
  1. Click "Save" on the top right
![admin page 3](readme_imgs/maint_mode_03.png?raw=true "admin page 3")
### Step 4: Users will now see a message similar to below when trying to view a map
![admin page 4](readme_imgs/maint_mode_04.png?raw=true "admin page 4")

# Mappable file types

_Note: Currently an API endpoint exists on the WorldMap to visualize Geotiff files.  However, the requisite Dataverse and Geoconnect code is not in place._

The mappability of different Dataverse file types can be switched on and off.  For example, the ability to map shapefiles may be turned off and the ability to view tabular files turned on.

![file types](readme_imgs/file_types.png?raw=true "file types")

  - For the current state of file types, see: https://geoconnect.datascience.iq.harvard.edu/dv/filetype-list/
  - To turn file mappability on/off, follow these steps:

### Step 1: Go to the geoconnect administrative interface.
### Step 2: Click "Incoming file type settings"
![file type 1](readme_imgs/file_type_admin_01.png?raw=true "file type 1")
### Step 3: Click the file type to change
![file type 2](readme_imgs/file_type_admin_02.png?raw=true "file type 2")
### Step 4: Change the setting
  1. Check "active" to enable/disable the file type
  2. Click "Save" on the top right

# Colors for Layer Styling

Colors, known to WorldMap as "color ramps" used for layer classification/styling may be set through the administrative interface.

To the user, the color choices appear in the dropdown shown below:

![color ui](readme_imgs/color_ui.png?raw=true "color ui")

## Changing color choices:

### Step 1: Go to the geoconnect administrative interface.
### Step 2: Click "Color ramps"
![color 1](readme_imgs/color_admin_01.png?raw=true "color 1")
### Step 3: Click on an existing color or click "Add Color Ramp"
![color 2](readme_imgs/color_admin_02.png?raw=true "color 2")
### Step 4: Modifying values
For the "Value name", always use `Custom` when specifying your own start color and end color.  
  - Once your changes are saved, they should appear in the Geoconnect color dropdown after reloading the web page.
  - Instead of deleting color choices, you can uncheck the "active" checkbox to hide color choices.
![color 3](readme_imgs/color_admin_03.png?raw=true "color 3")

### How colors correspond to Geoserver's SLD Service
Note: The value name, start color, and end color correspond to geoserver SLD service values described here: http://docs.geoserver.org/stable/en/user/community/sldservice/index.html#classify-vector-data
  - Geoconnect *Value name* -> *ramp* parameter.  
    - Possible values: `red`, `blue`, `gray`, `jet`, `random`, `custom`
    - Note: All of the values above _except_ `custom` will override the start and end color choices.
  - Geoconnect *Start color* -> *startColor* parameter
  - Geoconnect *End color* -> *endColor* parameter
  - _Note: The current version of WorldMap's geoserver does not support a `midColor`._

# WorldMap Join Targets

The WorldMap supplies target layers--or **JoinTargets** that a tabular file may be mapped against.  

- A list of current join targets may be found here: https://geoconnect.datascience.iq.harvard.edu/worldmap/show-jointarget-info/

A JSON description of these CGA curated **JoinTargets** may be retrieved via API

- **WorldMap** API endpoint: http://worldmap.harvard.edu/datatables/api/jointargets/
- **Note**: Login required (may be any WorldMap account credentials via HTTP Basic Auth)

- Example of JoinTarget information returned via the API:

```json
{
"data":[
  {
    "layer":"geonode:census_tracts_2010_boston_6f6",
    "name":"Census Tracts, Boston (GEOID10: State+County+Tract)",
    "geocode_type_slug":"us-census-tract",
    "geocode_type":"US Census Tract",
    "attribute":{
      "attribute":"CT_ID_10",
      "type":"xsd:string"
    },
    "abstract":"As of the 2010 census, Boston, MA contains 7,288 city blocks [truncated for example]",
    "title":"Census Tracts 2010, Boston (BARI)",
    "expected_format":{
      "expected_zero_padded_length":-1,
      "is_zero_padded":false,
      "description":"Concatenation of state, county and tract for 2010 Census Tracts.  Reference: https://www.census.gov/geo/maps-data/data/tract_rel_layout.html\r\n\r\nNote:  Across the US, this can be a zero-padded \"string\" but the original Boston layer has this column as \"numeric\" ",
      "name":"2010 Census Boston GEOID10 (State+County+Tract)"
    },
    "year":2010,
    "id":28
  },
  {
    "layer":"geonode:addresses_2014_boston_1wr",
    "name":"Addresses, Boston",
    "geocode_type_slug":"boston-administrative-geography",
    "geocode_type":"Boston, Administrative Geography",
    "attribute":{
      "attribute":"LocationID",
      "type":"xsd:int"
    },
    "abstract":"Unique addresses present in the parcels data set, which itself is derived from [truncated for example]",
    "title":"Addresses 2015, Boston (BARI)",
    "expected_format":{
      "expected_zero_padded_length":-1,
      "is_zero_padded":false,
      "description":"Boston, Administrative Geography, Boston Address Location ID.  Example: 1, 2, 3...nearly 120000",
      "name":"Boston Address Location ID (integer)"
    },
    "year":2015,
    "id":18
  },
  {
    "layer":"geonode:bra_neighborhood_statistical_areas_2012__ug9",
    "name":"BRA Neighborhood Statistical Areas, Boston",
    "geocode_type_slug":"boston-administrative-geography",
    "geocode_type":"Boston, Administrative Geography",
    "attribute":{
      "attribute":"BOSNA_R_ID",
      "type":"xsd:double"
    },
    "abstract":"BRA Neighborhood Statistical Areas 2015, Boston. Provided by [truncated for example]",
    "title":"BRA Neighborhood Statistical Areas 2015, Boston (BARI)",
    "expected_format":{
      "expected_zero_padded_length":-1,
      "is_zero_padded":false,
      "description":"Boston, Administrative Geography, Boston BRA Neighborhood Statistical Area ID (integer).  Examples: 1, 2, 3, ... 68, 69",
      "name":"Boston BRA Neighborhood Statistical Area ID (integer)"
    },
    "year":2015,
    "id":17
  }
],
"success":true
}
```

## How Geoconnect utilizes this info

When a user attempts to map a tabular file, the application looks in the Geoconnect database for JoinTargetInformation.  If this information is more than 10 minutes* old, the application will retrieve fresh information and save it to the db.  
(* change the timing via the variable ```JOIN_TARGET_UPDATE_TIME```)

This JoinTarget info is used to populate HTML forms used to match a tabular file column to a JoinTarget column.  Once a JoinTarget is chosen, the JoinTarget id is an essential piece of information used to make an API call to the WorldMap and attempt to map the file.

### Geoconnect Code for calling the API endpoint

- https://github.com/IQSS/geoconnect/blob/master/gc_apps/worldmap_connect/dataverse_layer_services.py#L275
- If link above has wrong line, search for ```def get_join_targets()```

### Geoconnect Code for saving the JoinTargetInformation

 - https://github.com/IQSS/geoconnect/blob/master/gc_apps/worldmap_connect/utils.py#L16
 - If link above has wrong line, search for ```def get_latest_jointarget_information()```

 # Tabular Column Formatting

In several cases of mapping tabular data, Geoconnect will add a formatted column to the Dataverse file before sending it to the WorldMap for visualization.  In these cases:
  - The file on Dataverse _is not changed_.  
  - However, the WorldMap will have a copy of the Dataverse data _with the extra, formatted column_
    - Within WorldMap, the tabular file is converted to a Postgres table.

## Cases Where Geoconnect Adds a "Formatted" Column

|#|DV Tabular File - Column Type|WorldMap layer - Column Type|Target Layer is Zero Padded?|Geoconnect Action|
---|:---:|:---:|:---:|---|
|1|Numeric|String|No|**Add formatted column**. Convert numeric to character--make it a string|
|2|Numeric|String|**Yes**|**Add formatted column**. Convert numeric to character. Add leading zeros to JoinTarget specified length|
|3|String|String|No|No Action|
|4|String|String|**Yes**|**Add formatted column**. Add leading zeros to JoinTarget specified length|
|5|String|Numeric|not applicable|No Action (currently)|
|6|Numeric|Numeric|not applicable|No Action|

## Background

### When mapping a tabular file GeoConnect sends the following information to WorldMap:
  1. DV Tabular File
  1. DV Tabular File Column Name for join
  1. JoinTarget id (JoinTarget objects in WorldMap include the join layer and the column to join on)
  1. DataverseInfo - metadata about the Dataverse file including the Dataverse, Dataset, file, description, name, etc--over 20 pieces of info

### Once the information is received, the WorldMap (roughly) takes the following actions:
  1. Verifies that the JoinTarget exists
  1. Checks if the join columns on the Tabular File and WorldMap layer are compatible  
  1. Converts the tabular file into a new Postgres table.  (A Datatable object within WorldMap)
  1. Attempts a SQL join between the new Postgres table and the existing Layer

### In some cases, a Dataverse join column will need formatting

Most often, this is in the case of the JoinTarget requiring leading zeros.

For example:
  - The Dataverse tabular file contains a 5-digit zip code column, but the leading leading zeros have been lost.  
    - e.g. "2476" instead of "02476"
  - The WorldMap JoinTarget specifies zero-padding and a length of 5--for a 5-digit zip code

In the example above, before sending the file to WorldMap, Geoconnect will take the following actions:
  - Create a new "formatted" column consisting of zero padded zip code values.  
    - e.g. In the new column, "2476" is converted to "02476"
  - Designate this new formatted column as the join column
