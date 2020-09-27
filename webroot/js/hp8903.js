
function measure_success(data, textStatus, jqXHR) {
    $("#output_image").attr("src", "data:image/png;base64," + data);
}

function measure(url, type, steps, freq1, freq2, amp1, amp2) {
    $("#start-measurement").prop("disabled",true);
    $.ajax({
        url: url,
        type: 'post',
        data: {
            type: type,
            steps: steps,
            freq1: freq1,
            freq2: freq2,
            amp1: amp1,
            amp2: amp2
        },
        headers: { 'x-content-encoding': 'base64' },
        success: measure_success
    }).fail(function(jqXHR, textStatus, errorThrown) {
        alert("AJAX request failed: " + textStatus + "\n" + errorThrown);
    }).always(function() {
        $("#start-measurement").prop("disabled", false);
    })
}

function init_hp8903() {
    $( "#measure-form" ).submit(function( event ) {
        // Stop form from submitting normally
        event.preventDefault();

        // Get some values from elements on the page:
        var $form = $( this ),
        type = $form.find( "select[name='type']" ).val(),
        steps = $form.find( "input[name='steps']" ).val(),
        freq1 = $form.find( "input[name='freq1']" ).val(),
        freq2 = $form.find( "input[name='freq2']" ).val(),
        amp1 = $form.find( "input[name='amp1']" ).val(),
        amp2 = $form.find( "input[name='amp2']" ).val()

        url = $form.attr( "action" );

        measure(url, type, steps, freq1, freq2, amp1, amp2);
    });
}