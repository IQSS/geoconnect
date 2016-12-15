/** Common functions used for geoconnect mapping
  (file: geoconnect_common.js)
*/

/* ----------------------------------------
    Same as console.log(...)
---------------------------------------- */
function logit(m){
    console.log(m);
}

/* ----------------------------------------
    Format HTML for a bootstrap alert
    - alert_type: success, info, warning or danger
---------------------------------------- */
function get_alert(alert_type, err_msg){
    return '<div class="alert alert-' + alert_type + ' alert-dismissible" role="alert"><button type="button" class="close" data-dismiss="alert"><span aria-hidden="true">&times;</span><span class="sr-only">Close</span></button>' + err_msg + '</div>';
}

/* ----------------------------------------
    Text for button after it is clicked
---------------------------------------- */
function getWorkingBtnMessage(){
    return 'Working ... (This may take up to 45 seconds)';
}

/* ----------------------------------------
   After a file is successfully mapped,
   process the JSON response and update:
     (1) alert message
     (2) map area
     (3) title panel
     (4) breadcrumb
---------------------------------------- */
function show_map_update_titles(json_resp){
    logit(json_resp.message);
    logit('exists? #msg_init_mapping_form:' + $('#msg_init_mapping_form').length)
    logit('exists? #id_alert_container:' + $('#id_alert_container').length)

    // Update message
    /*if ($('#msg_init_mapping_form').length){
        $('#msg_init_mapping_form').show().empty().append(get_alert('success', json_resp.data.message));
    }*/
    if ($('#id_alert_container').length){
        $('#id_alert_container').show().empty().append(get_alert('success', json_resp.data.message));
    }
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
