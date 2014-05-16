### GeoConnect sends Shapefile to WorldMap for Import

### Basic Flow
+ GeoConnect POSTs shapefile and metadata to WorldMap
+ On success, WorldMap (WM) returns metadata including a layer name and link
+ On fail, WM provides an error message
+ Worldmap proof of concept: [Django view](https://github.com/mbertrand/cga-worldmap/blob/dvn/geonode/dvn/views.py),
[Django url](https://github.com/mbertrand/cga-worldmap/blob/dvn/geonode/dvn/urls.py)

###  Input:  POST to WorldMap

Send a POST that includes a shapefile for WorldMap to import.

1. **title** - from dataverse metadata
1. **abstract** - from dataverse metadata
1. **email** - from dataverse user    
  + Use email to find existing WorldMap user or
  + Create new WorldMap user
  + 1st round: skip any confirmation steps in this process
1. **shapefile_name** - name of shapefile to import.  This is a .zip containing 1 shapefile
1. **content** - filestream of a .zip containing 1 shapefile
1. **geoconnect_token**  - “secret” string token to identify client. 
  + Used for proof of concept
  + This will be “upgraded” to oauth or similar protocol    
1. **worldmap_username** - optional.  2nd step, if it is available

### Output: JSON response

The JSON response depends on the outcome of the POST.  Roughly follow the JSend response guidelines for “success”, “fail”, and “error.”  (Note, probably won't use "error", just "fail")

#### On Success: New Layer and/or Map Created in WorldMap

1. **status** - "success"
1. **layer_name** - string with layer name
1.  **layer_link** - link to layer on WorldMap.  
  + Fully qualified url preferable
  + May be test server or alternate installation of WorldMap
1.  **worldmap_username** 
  + Created or retrieved based on email or worldmap_username in POST
  + Necessary for proof of concept?
1.  **embed_map_link** - link to map on WorldMap
   + Requires user to be created
   + Necessary for proof of concept?

#### On Fail:  Invalid data or call conditions

1. **status** - "fail"
2. **data** - hash with user readable messages
  +   Example: {   "status" : "fail",  
        "data" : { "title" : "A title is required" }  
    }

Full Specifications originally from a [google doc](https://docs.google.com/a/g.harvard.edu/document/d/1ASSQUaZoW_R1VqsMC5qZBCw1naEWw4yUOBLr_ACo3IM/)

