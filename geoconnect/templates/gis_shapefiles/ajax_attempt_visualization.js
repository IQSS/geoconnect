  /*
    This is called from the shapefile page when a user
    clicks "Visualize on Worldmap"
    Note: "success" HTML generated at ViewAjaxVisualizeShapefile.get()
  */
  function attempt_visualization(){

//      return;
    $("#id_main_panel_content").html($("#id_div_attempt_visualization_msg").html());

        var attempt_to_visualize_url = '{% url 'view_ajax_attempt_visualization' shapefile_info.md5 %}';
        var jqxhr = $.get(attempt_to_visualize_url, function(json_resp){

              console.log(json_resp);
           })
           .done(function(json_resp) {
               if (json_resp.success){
                   show_map_update_titles(json_resp);
                   //$('#id_progress_bar').hide();
               }else{
                   logit(json_resp.message);
                   $('#id_main_panel_content').show().empty().append(get_alert('danger', json_resp.message));
               }
            })
    }

  $(document).ready(function() {
        $("#id_link_visualize_worldmap").on( "click", attempt_visualization );
   });
