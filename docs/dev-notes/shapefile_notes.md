- Examine shapefile
    - view_01_examine_zip.html

## Shapefiles

### Basic view: view_02_single_shapefile.html

### Pre-Mapping:

view_02_single_shapefile.html

- Includes:
    - Title: "view_02_main_panel_title.html"
    - View: "view_02a_shp_table.html"
    - On error: "view_02a_err_examine.html"
    - Link back to Dataverse: "link-back-to-dataverse.html"

### Post-Mapping/Classify

view_02_single_shapefile.html

- Includes:
    - View/Classify: "view_04_ajax_style_layer.html"
    - Delete Confirmation (Modal): "modal_delete_confirm.html"
    - Save Confirmation (Modal): "modal_save_confirm.html"
    - Classify JS: "classification/classify_form_dynamic_js.html"
- Ajax:
    - view: view_classify_layer_form
        - template(s):
            - classification/view_classify_form.html
            - classification/classify_success_msg.html
            - classification/classify_major_error.html
            - classification/classify_basic_error.html
- Views:
    - view_classify_layer_form (classification/views.py)
    - view_delete_map (gis_shapefiles/views_delete.py)
