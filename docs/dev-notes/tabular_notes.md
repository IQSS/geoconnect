# Tabular Files

## Workflow, 1st Time File, No Map exists

1. view: ```view_mapit_incoming_token64```
  - file: ```gis_shapefiles/views_mapit.py```
1. redirect function: ```process_tabular_file_info```
  - file: ```gis_shapefiles/views_mapit.py```
1. view: ```view_tabular_file(tab_md5)```
  - file: ```gis_tabular/views.py```   
  - Note: Will check if geoconnect already has this map
  - TO ADD: Check WorldMap directly for this map
  - ** Template Info**
    1. main template: ```gis_tabular/view_tabular_overview.html```
      - expected values:
        - tabular_info
        - geocode_types
        - form_lat_lng (always)
        - form_single_column (optional)

    2. sub template: ```gis_tabular/preview_rows.html```
      - expected values:
        - tabular_info
        - NUM_PREVIEW_ROWS
        - tab_file_stats


## Workflow, 1st Time File, Attempt to Create Join

1. ajax view: ```view_map_tabular_file_form```
  - file: ```gis_tabular/views_create_layer.py```

### Successful join: Create view with Map and Classify Form

  - view: ```build_tabular_map_html```(WorldMapTabularLayerInfo)
  - file: ```gis_tabular.views.py```
  - main template: ```gis_tabular/view_tabular_map_div.html```
    - expected values (directly in template):
      1. layer_data
      1. worldmap_layerinfo
      1. download_links

All expected values in template and sub-templates:
  1. worldmap_layerinfo (WorldMapJoinLayerInfo or WorldMapLatLngInfo )
  1. tabular_info (worldmap_layerinfo.tabular_info)
  1. core_data (worldmap_layerinfo.core_data)
  1. download_links (worldmap_layerinfo.download_links)
  1. attribute_data (worldmap_layerinfo.attribute_data)
  1. is_tabular_delete (set in view)
  1. delete_form (set in view)
  1. classify_form (set in view)
  1. ATTRIBUTE_VALUE_DELIMITER (set in view)
  1. success_msg or error_msg   


**Template hierarchy:**

  1. ```gis_tabular/map_result_message.html```
    - expected values:
      1. worldmap_layerinfo
    - ```gis_tabular/map_message_join.html```
      - expected values:
        1. core_data (worldmap_layerinfo.core_data)
    - ```gis_tabular/map_message_lat_lng.html```
      - expected values:
        1. core_data (worldmap_layerinfo.core_data)
  1. ```gis_shapefiles/modal_delete_confirm.html```
    - expected values:
      1. is_tabular_delete
      1. delete_form
  1. ```gis_shapefiles/modal_save_confirm.html```
    - expected values:
      1. tabular_info
  1. ```classification/view_classify_form.html```
    - expected values:
      1. classify_form
      1. success_msg or error_msg                      
  1. ```classification/classify_form_dynamic_js.html```
    - expected values:
      1. worldmap_layerinfo
        1. worldmap_layerinfo.get_legend_img_url
      1. classify_form
        1. classify_form.get_classify_non_string_choices
        1. classify_form.get_classify_choices
        1. classify_form.get_classify_string_choices
        1. ATTRIBUTE_VALUE_DELIMITER
  1. ```gis_shapefiles/delete_and_back_to_dv_links.html```
    - ```gis_shapefiles/link-back-to-dataverse.html```
      - expected values:
        1. tabular_info
        1. tabular_info.return_to_dataverse_url
  1. ```gis_tabular/map_attributes_list.html``` (debug)
    - expected values:
      1. attribute_data (worldmap_layerinfo.attribute_data)
      1. core_data (worldmap_layerinfo.core_data)
  1. ```gis_tabular/core_data_list.html``` (debug)
    - expected values:
      1. core_data (worldmap_layerinfo.core_data)


## Workflow, Classify a Tabular File

- **ajax view**: ```view_classify_layer_form```
- **file:** ```classification/views.py```

- The request fails form ValidationError message contents (JSON):
    { "success": false
      "msg": User message
      "data.div_content": Form with error messages }

    - "div_content" in AJAX message is used for "#div_classify_form"

- The request succeeds:
    { "success": true
    "msg": User message
    "data.div_content": _See note below_ }

  - Note: template for div_content: ```classification/view_classify_form.html```
    - expected values:
      1. classify_form
      1. success_msg or error_msg   
