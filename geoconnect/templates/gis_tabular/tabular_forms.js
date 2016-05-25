<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.10/css/jquery.dataTables.css">
<script type="text/javascript" charset="utf8" src="https://cdn.datatables.net/1.10.10/js/jquery.dataTables.js"></script>
<script>

    function get_alert(alert_type, err_msg){
        return '<div class="alert alert-' + alert_type + ' alert-dismissible" role="alert"><button type="button" class="close" data-dismiss="alert"><span aria-hidden="true">&times;</span><span class="sr-only">Close</span></button>' + err_msg + '</div>';
    }

    function getWorkingBtnMessage(){
        return 'Working ... (This may take up to 45 seconds)';
    }
    /* ------------------------------------------
        Submit the latitude/longitude form
    ------------------------------------------ */
    function submit_lat_lng_form(){
        console.log('submit_lat_lng_form');

        // url for ajax  call
        check_lat_lng_url = '{% url 'view_process_lat_lng_form' %}';

        // Disable submit button + hide message box
        $('#id_frm_lat_lng_submit').addClass('disabled').html(getWorkingBtnMessage());
        $('#msg_form_tabular').empty().hide();

        // Submit form
        var jqxhr = $.post(check_lat_lng_url, $('#form_map_tabular_file').serialize(), function(json_resp) {
            // don't need a response for user
            console.log(json_resp);
        })
        .done(function(json_resp) {
            if (json_resp.success){
                // Show map, update titles
                show_map_update_titles(json_resp);
                //$('#msg_form_tabular').show().empty().append(get_alert('success', json_resp.message));
                //if (json_resp.data.map_html){
                //    $('#id_main_panel_content').html(json_resp.data.map_html);
                //    $('#id_main_panel_title').html('you did it');
                //}

            }else{
                console.log(json_resp.message);
                // form error, display message
                //$('#msg_form_lat_lng').html(json_resp.message);
                $('#msg_form_tabular').show().empty().append(get_alert('danger', json_resp.message));

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

        console.log('update_target_layers_based_on_geotype');
        if (selected_geocode_type.length == 0){
            return;
        }
        // form url to make request
        target_layers_by_type_url = '{% url 'ajax_get_all_join_targets' %}' + selected_geocode_type;

        // Temporarily disable layer dropdown box
        $('#id_chosen_layer').addClass('disabled');
        // Disable submit button
        $('#id_frm_single_column_submit').addClass('disabled').html('Working...');

        // Submit form
        var jqxhr = $.get(target_layers_by_type_url, function(json_resp) {
            // don't need a response for user
            console.log(json_resp);
        })
        .done(function(json_resp) {
            if (json_resp.success && json_resp.data){
                console.log('success!!' + json_resp.data);
                // {"message": "success", "data": [[9, "US Census Tract (2000) Boston Census Blocks"]], "success": true}
                // Update the dropdown box

                // Clear options from dropdown
                $('#id_chosen_layer')
                    .find('option').remove().end();

                // Add new options
                $.each(json_resp.data, function (index, item) {
                    $('#id_chosen_layer')
                        .append('<option value="' + item[0] + '">' + item[1] + '</option>');
                });

            }else{
                console.log(json_resp.message);
                // form error, display message
                //$('#msg_form_lat_lng').html(json_resp.message);
                $('#msg_form_tabular').show().empty().append(get_alert('danger', json_resp.message));

            }
          })
        .fail(function(json_resp) {
        })
        .always(function() {
            // Enable dropdown
            $('#id_chosen_layer').removeClass('disabled');
            // Enable submit button
            $('#id_frm_single_column_submit').removeClass('disabled').html('Submit');

        });
        //alert(target_layers_by_type_url);
    }

    function show_map_update_titles(json_resp){

        // Update message
        $('#msg_form_tabular').show().empty().append(get_alert('success', json_resp.message));

        // Show map
        if (json_resp.data.hasOwnProperty('map_html')){
            $('#id_main_panel_content').html(json_resp.data.map_html);
        }
        // Title update
        if (json_resp.data.hasOwnProperty('id_main_panel_title')){
             //$("#id_main_panel_title").html(json_resp.data.id_main_panel_title);
             $("#id_main_panel_title").replaceWith(json_resp.data.id_main_panel_title);
        }
        // Breadcrumb update
        if(json_resp.data.hasOwnProperty('id_breadcrumb')){
            $( "#id_breadcrumb" ).replaceWith(json_resp.data.id_breadcrumb);
        }

    }

    function submit_single_column_form(){
        console.log('submit_single_column_form');

        // url for ajax  call
        map_tabular_file_url = '{% url 'view_map_tabular_file_form' %}';

        // Disable submit button + hide message box
        $('#id_frm_single_column_submit').addClass('disabled').html(getWorkingBtnMessage());
        $('#msg_form_tabular').empty().hide();

        // Submit form
        var jqxhr = $.post(map_tabular_file_url, $('#form_map_tabular_file').serialize(), function(json_resp) {
            // don't need a response for user
            console.log(json_resp);
        })
        .done(function(json_resp) {
            if (json_resp.success){
                show_map_update_titles(json_resp);
                //$('#id_progress_bar').hide();
            }else{
                console.log(json_resp.message);
                $('#msg_form_tabular').show().empty().append(get_alert('danger', json_resp.message));

            }
          })
        .fail(function(json_resp) {
             //$('#simple_msg_div').empty().append(get_alert('danger', 'The classification failed.  Please try again.'));
        })
        .always(function() {
             // Enable submit button
             if ($('#id_frm_single_column_submit').length){
                 $('#id_frm_single_column_submit').removeClass('disabled').html('Submit');
             }
        });
    }

    function bind_form_submit_buttons(){
        //console.log('bind_submit_lat_lng_form');
        $("#id_frm_lat_lng_submit").on( "click", submit_lat_lng_form );
        $("#id_frm_single_column_submit").on( "click", submit_single_column_form );
    }

    function bind_hide_show_column_forms(){
        console.log('bind geotype dropdown');
        $( "#id_geocode_type" ).change(function() {

            geocode_type_val = $( "#id_geocode_type" ).val()
            console.log('type: '+ geocode_type_val);
            if (geocode_type_val == '{{ GEO_TYPE_LATITUDE_LONGITUDE }}'){
                // show latitude-longitude form
                $('.form_inactive_default').hide();
                $('.form_lat_lng_fields').show();
                $('.form_single_column_fields').hide();

            }else if (geocode_type_val == ''){
                // hide both forms

                $('.form_inactive_default').show();
                $('.form_lat_lng_fields').hide();
                $('.form_single_column_fields').hide();

            }else{
                // show single column form
                update_target_layers_based_on_geotype(geocode_type_val);
                $('.form_inactive_default').hide();
                $('.form_lat_lng_fields').hide();
                $('.form_single_column_fields').show();
                $("label[for='id_chosen_column']").html('Column for "' + $( "#id_geocode_type option:selected" ).html() + '"');

            }
        });
    }

    $( document ).ready(function() {
        bind_hide_show_column_forms();
        bind_form_submit_buttons();
        //$( "#id_geocode_type" ).change(function() {
          //alert( "Handler for .change() called." + $( "#id_geocode_type" ).val() );
        //});
        $('#preview-tbl').DataTable( {
                "scrollY": 400,
                "scrollX": true,
                "paging" : false,
                "searching" : false
        } );
        //$('#preview-tbl').DataTable();
    });
</script>
