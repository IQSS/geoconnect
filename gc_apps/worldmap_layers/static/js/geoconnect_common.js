/** Common functions used for geoconnect mapping
  (file: geoconnect_common.js)
*/

var INITIAL_SELECT_CHOICE = 'Select...';

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
    return '<div class="alert alert-' + alert_type + ' alert-dismissible small" role="alert" style="margin-left:auto;margin-right:auto;"><button type="button" class="close" data-dismiss="alert"><span aria-hidden="true">&times;</span><span class="sr-only">Close</span></button>' + err_msg + '</div>';
}

/* ----------------------------------------
    Text for button after it is clicked
---------------------------------------- */
function getWorkingBtnMessage(){
    return 'Working... (This may take up to 45 seconds)';
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
    logit(json_resp.data);

    if ($('#id_alert_container').length){
        // json_resp.data.user_message_html is already formatted HTML
        $('#id_alert_container').show().empty().append(json_resp.data.user_message_html);
        //var user_alert_msg = get_alert('success', json_resp.data.user_message_html);
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

}
