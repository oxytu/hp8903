
function measure_success(data, textStatus, jqXHR) {
    if ($("#keep-measurements").val()) {
        $("#output_image").clone().prepend("#output_old");
    }
    $("#output_image").attr("src", "data:image/png;base64," + data);
}

function measure(url, type, steps, freq1, freq2, amp1, amp2, title) {
    $("#start-measurement").prop("disabled",true);
    $("#measurement-in-progress").show();
    $.ajax({
        url: url,
        type: 'post',
        data: {
            type: type,
            steps: steps,
            freq1: freq1,
            freq2: freq2,
            amp1: amp1,
            amp2: amp2,
            title: title
        },
        headers: { 'x-content-encoding': 'base64' },
        success: measure_success
    }).fail(function(jqXHR, textStatus, errorThrown) {
        alert("AJAX request failed: " + textStatus + "\n" + errorThrown);
    }).always(function() {
        $("#start-measurement").prop("disabled", false);
        $("#measurement-in-progress").hide();
    })
}

function submit_measure(this, event) {
    // Stop form from submitting normally
    event.preventDefault();

    // Get some values from elements on the page:
    var $form = this,
    type = $form.find( "select[name='type']" ).val(),
    steps = $form.find( "input[name='steps']" ).val(),
    freq1 = $form.find( "input[name='freq1']" ).val(),
    freq2 = $form.find( "input[name='freq2']" ).val(),
    amp1 = $form.find( "input[name='amp1']" ).val(),
    amp2 = $form.find( "input[name='amp2']" ).val(),
    title = $form.find( "input[name='title']" ).val()

    url = $form.attr( "action" );

    measure(url, type, steps, freq1, freq2, amp1, amp2, title);
}

function init_hp8903() {
    $( "#measure-form" ).submit(function( event ) {
        submit_measure($(this), event);
    });
}