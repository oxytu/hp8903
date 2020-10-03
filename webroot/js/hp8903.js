
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
    return $.ajax({
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
    
    freq_steps = $form.find( "input[name='freq-steps']" ).val(),
    freq = $form.find( "input[name='freq']" ).val(),
    freq1 = $form.find( "input[name='freq1']" ).val(),
    freq2 = $form.find( "input[name='freq2']" ).val(),

    amp_steps = $form.find( "input[name='amp-steps']" ).val(),
    amp = $form.find( "input[name='amp']" ).val(),
    amp1 = $form.find( "input[name='amp1']" ).val(),
    amp2 = $form.find( "input[name='amp2']" ).val(),

    title = $form.find( "input[name='title']" ).val()

    url = $form.attr( "action" );

    var steps = 1;

    if (type.endsWith("_LVL")) {
        freq1 = freq;
        // freq2 is ignored in implementation
        steps = amp_steps;
    } else if (type.endsWith("_FRQ")) {
        amp1 = amp;
        // amp2 is ignored in implementation
        steps = freq_steps;
    } else if (type.startsWith("MULTI_")) {
        if (type == "MULTI_FR_THD") {
            measure(url, "LVL_FRQ", freq_steps, freq1, freq2, amp, amp2, title + " (Freq. Resp.)").then(
            measure(url, "THDLV_LVL", amp_steps, freq, freq2, amp1, amp2, title + " (Clipping Behaviour)")).then(
            measure(url, "THDLV_FRQ", freq_steps, freq1, freq2, amp, amp2, title + " (THD+N)"));
        }
        return
    }

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

function show_hide_formcontrols() {
    var measurement = $("#type").val();
    if (measurement.endsWith("_FRQ")) {
        //.find(':input').prop("disabled", false)
        $(".amp-static").show();
        $(".amp-sweep").hide();

        $(".freq-static").hide();
        $(".freq-sweep").show();
    } else if (measurement.endsWith("_LVL")) {
        $(".amp-static").hide();
        $(".amp-sweep").show();

        $(".freq-static").show();
        $(".freq-sweep").hide();
    } else if (measurement.startsWith("MULTI_")) {
        $(".amp-static").show();
        $(".amp-sweep").show();

        $(".freq-static").show();
        $(".freq-sweep").show();
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

    $("#type").change(function() { show_hide_formcontrols() });

    show_hide_formcontrols();

    restoreLocalStorageState();

}