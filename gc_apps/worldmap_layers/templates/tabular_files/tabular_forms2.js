<script>
/**
 *  1.19.2017
 *  This became a bit messy--two forms in the backend and the front end changed
 *  resulting in the form elements being separated, etc.
 *
 *  submit lat/lng form
 *    - 2 dropdowns to specifiying lat/lng columns
 *    - submit button
 *  submit join column form
 *    - 3 dropdowns: geo type, worldmap layer, column to join on
 *      - id_geocode_type
 *      - id_chosen_column
 *      - id_chosen_layer
 *    - submit button
 *
 *  Action:
 *      init: only geo type dropdown shows
 */
 function logit2(m){
     {% if DEBUG_MODE %}
        console.log(m);
     {% else %}
        // Write to console when Django DEBUG=True
     {% endif %}
 }

    var SUBMIT_BUTTON_TEXT = 'Submit Data to WorldMap'
    var INITIAL_SELECT_CHOICE = 'Select...';
    var DEFAULT_LAYER_DESCRIPTION = 'This is a brief description about the layer.';
    var LAYER_DESCRIPTIONS;

    /* ------------------------------------------
        Submit the latitude/longitude form
    ------------------------------------------ */
    function submit_lat_lng_form(){
        logit2('submit_lat_lng_form');

        // url for ajax  call
        check_lat_lng_url = '{% url 'view_process_lat_lng_form' %}';

        // Disable submit button + hide message box
        $('#id_frm_lat_lng_submit').addClass('disabled').html(getWorkingBtnMessage());
        $('#id_alert_container').empty().hide();

        // Submit form
        var jqxhr = $.post(check_lat_lng_url, $('#form_map_tabular_file').serialize(), function(json_resp) {
            // don't need a response for user
            logit2(json_resp);
        })
        .done(function(json_resp) {
            if (json_resp.success){
                // Show map, update titles
                show_map_update_titles(json_resp);
                $('#id_preview_table_panel').hide();    // hide the preview table
                hide_setup_form_submit_buttons();
                window.scrollTo(0, 0);
            }else{
                logit2(json_resp.message);
                // form error, display message
                //$('#msg_form_lat_lng').html(json_resp.message);
                $('#id_alert_container').show().empty().append(get_alert('danger', json_resp.message));

            }
          })
        .fail(function(json_resp) {
             //$('#simple_msg_div').empty().append(get_alert('danger', 'The classification failed.  Please try again.'));
        })
        .always(function() {
             // Enable submit button
             if ($('#id_frm_lat_lng_submit').length){
                 $('#id_frm_lat_lng_submit').removeClass('disabled').html('Submit Latitude & Longitude columns');
             }
        });
    }



    /**
        The user has selected a new "Geosptial Data Type"
        Via Ajax, retrieve a list of layers that match this type.
    */
    function update_target_layers_based_on_geotype(selected_geocode_type){

        logit2('update_target_layers_based_on_geotype');
        if (selected_geocode_type.length == 0){
            clear_layer_description();
            return;
        }
        // form url to make request
        target_layers_by_type_url = '{% url 'ajax_get_all_join_targets_with_descriptions' %}' + selected_geocode_type;

        // Temporarily disable layer dropdown box
        $('#id_chosen_layer').addClass('disabled');
        // Disable submit button
        $('#id_frm_single_column_submit').addClass('disabled').html('Working...');

        // Submit form
        var jqxhr = $.get(target_layers_by_type_url, function(json_resp) {
            // don't need a response for user
            logit2(json_resp);
        })
        .done(function(json_resp) {
            if (json_resp.success && json_resp.data){

                logit2('success!!' + json_resp.data);
                // {"message": "success", "data": [[9, "US Census Tract (2000) Boston Census Blocks"]], "success": true}
                // Update the dropdown box

                // Clear options from dropdown
                $('#id_chosen_layer')
                    .find('option').remove().end();

                // Add top Select
                $('#id_chosen_layer')
                    .append('<option value="">' + INITIAL_SELECT_CHOICE + '</option>');

                // Add new options
                $.each(json_resp.data, function (index, item) {
                    $('#id_chosen_layer')
                        .append('<option value="' + item.join_target_id + '">' + item.name + '</option>');
                        //.append('<option value="' + item[0] + '">' + item[1] + '</option>');
                });

                // Save the data to a local variable
                LAYER_DESCRIPTIONS = json_resp.data;

                clear_layer_description();

            }else{
                logit2(json_resp.message);
                // form error, display message
                //$('#msg_form_lat_lng').html(json_resp.message);
                $('#id_alert_container').show().empty().append(get_alert('danger', json_resp.message));

            }
          })
        .fail(function(json_resp) {
        })
        .always(function() {
            // Enable dropdown
            $('#id_chosen_layer').removeClass('disabled');
            // Enable submit button
            $('#id_frm_single_column_submit').removeClass('disabled').html(SUBMIT_BUTTON_TEXT);


        });
        //alert(target_layers_by_type_url);
    }

    //----------------------------------------
    // clear layer description
    //----------------------------------------
    function clear_layer_description(){
        $('#id_layer_description').html(DEFAULT_LAYER_DESCRIPTION);
        $('#id_layer_description').addClass('text-muted');
    }

    /**
     * Called after successful mapping of a tabular file
     */
    function hide_setup_form_submit_buttons(){
        logit2('hide_setup_form_submit_buttons');
        $('#id_setup_form_buttons').hide();
    }

    function submit_single_column_form(){
        logit2('submit_single_column_form');

        // url for ajax  call
        map_tabular_file_url = '{% url 'view_map_tabular_file_form' %}';

        // Disable submit button + hide message box
        $('#id_frm_single_column_submit').addClass('disabled').html(getWorkingBtnMessage());
        $('#id_alert_container').empty().hide();

        // Submit form
        var jqxhr = $.post(map_tabular_file_url, $('#form_map_tabular_file').serialize(), function(json_resp) {
            // don't need a response for user
            logit2(json_resp);
        })
        .done(function(json_resp) {
            if (json_resp.success){
                $('#id_preview_table_panel').hide();    // hide the preview table
                show_map_update_titles(json_resp);
                hide_setup_form_submit_buttons();
                window.scrollTo(0, 0);
            }else{

                logit2(json_resp.message);
                $('#id_alert_container').show().empty().append(get_alert('danger', json_resp.message));

            }
          })
        .fail(function(json_resp) {
             //$('#simple_msg_div').empty().append(get_alert('danger', 'The classification failed.  Please try again.'));
        })
        .always(function() {
             // Enable submit button
             if ($('#id_frm_single_column_submit').length){
                 $('#id_frm_single_column_submit').removeClass('disabled').html(SUBMIT_BUTTON_TEXT);
             }
        });
    }

    function bind_form_submit_buttons(){
        logit2('bind_submit_lat_lng_form');
        $("#id_frm_lat_lng_submit").on( "click", submit_lat_lng_form );
        $("#id_frm_single_column_submit").on( "click", submit_single_column_form );
    }

    /**
     *  show cancel button without form submit buttons
     */
    function show_cancel_only_button(){
        logit2('show cancel button');
        $('#div_btn_cancel').show();
    }

    function hide_cancel_only_button(){
        logit2('HIDE cancel button');
        $('#div_btn_cancel').hide();
    }

    /**
     *  Hide row with select WorldMap layer dropdown
     */
    function hide_form_worldmap_layer_row(){
        $('.form_worldmap_layer').hide();
    }

    /**
     *  Show row with select WorldMap layer dropdown
     */
    function show_form_worldmap_layer_row(){
        $('.form_worldmap_layer').show();
    }

    /**
     *  id_row2_div_select_layer
     *
     */
    function really_bind_hide_show_column_forms(){

        hide_form_worldmap_layer_row();

        var geocode_type_val = $( "#id_geocode_type" ).val()
        logit2('type: '+ geocode_type_val);
        if (geocode_type_val == '{{ GEO_TYPE_LATITUDE_LONGITUDE }}'){
            // show latitude-longitude form
            $('.form_lat_lng_fields').show();
            $('.form_single_column_fields').hide();
            hide_form_worldmap_layer_row();
            clear_layer_description();
            hide_cancel_only_button();  //  hide cancel only button

        }else if (geocode_type_val == ''){      // RESET

            // hide both forms + show cancel button
            $('.form_lat_lng_fields').hide();
            $('.form_single_column_fields').hide();
            show_cancel_only_button();
            hide_form_worldmap_layer_row();
            clear_layer_description();

        }else{                                  // JOIN TO WORLDMAP LAYER
            // show single column form
            //update_target_layers_based_on_geotype(geocode_type_val);
            clear_layer_description();
            $('.form_lat_lng_fields').hide();
            $('.form_single_column_fields').show();
            check_join_column_change();
            //hide_cancel_only_button();  //  hide cancel only button
        }
    }

    /**
     *  If selected column has changed*, decide whether to:
     *  - show the worldmap layer dropdown
     *  - hide the worldmap layer dropdown
     *          * doesn't apply to the lat/lng form
     */
    function check_join_column_change(){

        var chosen_col_val = $( "#id_chosen_column" ).val();

        if (chosen_col_val == ''){
            hide_form_worldmap_layer_row();
            clear_layer_description();
            show_cancel_only_button();

        }else{
            show_form_worldmap_layer_row();
            var geocode_type_val = $( "#id_geocode_type" ).val()
            update_target_layers_based_on_geotype(geocode_type_val);
            hide_cancel_only_button();
            check_chosen_layer_change();
        }

    }


    /**
     *  If selected worldmap layer has changed, change description, if appropriate
     */
     function check_chosen_layer_change(){
        // ---------------------------------------
        // clear current description
        // ---------------------------------------
        clear_layer_description();

        // ---------------------------------------
        // Get the id of the chosen joinTarget
        // ---------------------------------------
        var chosen_layer_id = $( "#id_chosen_layer" ).val();

        // ---------------------------------------
        // If the id, is blank, set back to default
        // ---------------------------------------
        if (chosen_layer_id == ''){
            clear_layer_description();
            return;
        }

        // ---------------------------------------
        // Look for the layer description
        // ---------------------------------------
        var description_found = false;
        if (typeof LAYER_DESCRIPTIONS != 'undefined'){
            $.each(LAYER_DESCRIPTIONS, function (index, item) {
                if (chosen_layer_id==item.join_target_id){
                    logit2('found a description: ' + item.description);
                    // found a description
                    $("#id_layer_description").html(item.description);
                    $('#id_layer_description').removeClass('text-muted');
                    description_found = true;
                }
            });
        }

        // ---------------------------------------
        // Didn't find a description, go back to default
        // ---------------------------------------
        if (!description_found){
            clear_layer_description();
        }


    }


    function bind_hide_show_column_forms_on_ready(){
        really_bind_hide_show_column_forms();
    }

    /**
     *  What happens as users clicks through form elements
     */
    function bind_hide_show_column_forms_on_change(){

        // the geo type has changed
        //
        $( "#id_geocode_type" ).change(function() {
            really_bind_hide_show_column_forms();
            check_chosen_layer_change();
        });

        // the chosen column for a join has changed
        // and impacts the layer visibility
        //
        $( "#id_chosen_column" ).change(function() {
            // note: this then calls check_chosen_layer_change();
            check_join_column_change();
        });

        $( "#id_chosen_layer").change(function() {
            check_chosen_layer_change();
        });
    }


    /**
        Set the selected column option based on its value
    */
    function setNewSelectedCol(selectedText){
        var optToSelect = $('#id_chosen_column option[value="' +selectedText +'"]');
        if (typeof optToSelect === "undefined") {
            return;
        }
        optToSelect.prop('selected', true);
        check_join_column_change();
    }

    /**
      click preview table to select tabular column

      Disabled for now with reshifting of forms
    *//*
    function bind_select_column_by_preview_table_click(){

        // Click on the header column
        $(".geo_col_select").on('click', function() {
            var selectedHeaderText = $(this).html();
            logit2('clicked...:' + selectedHeaderText);
            setNewSelectedCol(selectedHeaderText);
        })

        // Click on the table body
        $("#preview-tbl tbody tr").on('click', 'td', function() {
              var colIdx = $(this).index();
              if (colIdx == 0) return;
              var colObj = $('#preview-tbl thead tr').find('th').eq(colIdx);
              var selectedHeaderText = colObj.find('div span').html();
              setNewSelectedCol(selectedHeaderText);
        });
    }*/

    $( document ).ready(function() {
        // bind events for form display
        bind_hide_show_column_forms_on_change();
        bind_hide_show_column_forms_on_ready();
        bind_form_submit_buttons();

        // click preview table to select tabular column
        //bind_select_column_by_preview_table_click();

        var previewTable = $('#preview-tbl').DataTable( {
                "searching" : false,
                "paging" : false,
                "info":false,
                "scrollX": true
        } );
    });
</script>
