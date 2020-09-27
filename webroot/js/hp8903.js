
function uniqId() {
    return Math.round(new Date().getTime() + (Math.random() * 10000));
  }

function measure_success(data, textStatus, jqXHR) {
    $("#output_measurement > .output_date").text("Date: " + new Date());
    $("#output_measurement > .output_image").attr("src", "data:image/png;base64," + data);
    
    if ($("#keep-measurements").prop('checked')) {
        $("#output_measurement").clone().prop('id', 'output_measurement_' + uniqId() ).prependTo("#output_old");
    }

    localStorage.setItem('measurements', $('#output_old').html());
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

function submit_measure(form, event) {
    // Stop form from submitting normally
    event.preventDefault();

    // Get some values from elements on the page:
    var $form = form,
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

function restoreLocalStorageState() {
    var measurements = localStorage.getItem("measurements");
    var keep_measurements = localStorage.getItem("keep-measurements");

    if (measurements != null) {
        $('#output_old').html(measurements);
    }
    if (keep_measurements != null) {
        $("#keep-measurements").prop('checked', keep_measurements);
    }
}

function init_hp8903() {
    $( "#measure-form" ).submit(function( event ) {
        submit_measure($(this), event);
    });

    $("#keep-measurements").click(function() {
        localStorage.setItem("keep-measurements", $("#keep-measurements").prop('checked'));
    });

    $("#output-clear-all").click(function() {
        localStorage.setItem("measurements", null);

        $('#output_old').html("");
    });

    restoreLocalStorageState();

}