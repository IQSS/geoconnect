
  function attempt_visualization(){

    $("#id_main_panel_content").html($("#id_div_attempt_visualization_msg").html());

        var attempt_to_visualize_url = '{% url 'view_ajax_attempt_visualization' shapefile_info.md5 %}';
        var jqxhr = $.get( attempt_to_visualize_url, function(json_resp) {

              console.log(json_resp);
              // If new form/message data is in the response, then update the page
             //  if ((json_resp.data)&&(json_resp.data.div_content)){
             //    $( "#div_classify_form" ).html(json_resp.data.div_content);
              //   $( "#id_frm_style_submit" ).on( "click", submit_classify_form );

              // }
           })    
           .done(function(json_resp) {
              if (json_resp.success){
                   // main panel update
                   if (json_resp.data.hasOwnProperty('id_main_panel_content')){
                        $("#id_main_panel_content").html(json_resp.data.id_main_panel_content);
                    }else{
                        $("#id_main_panel_content").html("Sorry! An error occurred!");
                    }
                    // title update
                    if (json_resp.data.hasOwnProperty('id_main_panel_title')){
                         //$("#id_main_panel_title").html(json_resp.data.id_main_panel_title);
                         $("#id_main_panel_title").replaceWith(json_resp.data.id_main_panel_title);
                    }                    
                    // breadcrumb update
                    if(json_resp.data.hasOwnProperty('id_breadcrumb')){
                        $( "#id_breadcrumb" ).replaceWith(json_resp.data.id_breadcrumb);
                    }
              }else{
                  if (json_resp.data.hasOwnProperty('id_main_panel_content')){
                      $("#id_main_panel_content").html(json_resp.data.id_main_panel_content);
                  }else{
                      $("#id_main_panel_content").html("Sorry! An error occurred!");
                  }
        //          message
                 // $('#simple_msg_div').show();
                 // $('#simple_msg_div').empty().append(get_alert('danger', json_resp.message));

              }
            })
    }

  $(document).ready(function() {
        $("#id_link_visualize_worldmap").on( "click", attempt_visualization );

//        $( "#id_breadcrumb" ).on( "click", submit_classify_form );
  //      $( "#id_attribute" ).on( "change", check_attribute );
    //    check_attribute();
   });
{% comment %}
function submit_classify_form(){

            // Fade out classify button
            $('#id_frm_style_submit').addClass('disabled').html('Working...');

           var classify_url = "{% url 'view_classify_layer_form' worldmap_layerinfo.md5 %}";
           var jqxhr = $.post( classify_url, $('#frm_classify').serialize(), function(json_resp) {

              // console.log(json_resp);
              // If new form/message data is in the response, then update the page
               if ((json_resp.data)&&(json_resp.data.div_content)){
                 $( "#div_classify_form" ).html(json_resp.data.div_content);
                 $( "#id_frm_style_submit" ).on( "click", submit_classify_form );

               }
           })
           .done(function(json_resp) {
               if (json_resp.success){
                    // Reload the map!
                   $( '#id_iframe_map' ).attr( 'src', function ( i, val ) { return val; });
                   $('#id_progress_bar').hide();

               }else{
                   $('#simple_msg_div').show();
                   $('#simple_msg_div').empty().append(get_alert('danger', json_resp.message));

               }
             })
           .fail(function(json_resp) {
                $('#simple_msg_div').show();
                $('#simple_msg_div').empty().append(get_alert('danger', 'The classification failed.  Please try again.'));
                $('#id_success_msg').hide();
                $('#id_alert_msg').hide();

           })
           .always(function() {
                // Restore classify button
                $('#id_frm_style_submit').removeClass('disabled').html('Style Layer');
                $( "#id_attribute" ).on( "change", check_attribute );

               //bind_form_submit_button();
           });
   }
   {% endcomment %}
