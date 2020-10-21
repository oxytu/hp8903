
function uniqId() {
    return Math.round(new Date().getTime() + (Math.random() * 10000));
  }

function measure_success(data, textStatus, jqXHR, title, csvData = null) {
    $("#output_measurement > .output_date").html("<b>" + title + "</b> - Date: " + new Date());
    var link = $("#output_measurement > .download_csv > .download_csv_link");

    if (csvData != null) {
        $("#output_measurement > .download_csv > .csv_content").text(csvData);
        link.mousedown(inject_download);
        link.attr('download', "measurement-" + title + ".csv");
    } else {
        link.hide();
    }
    $("#output_measurement > .output_image").attr("src", "data:image/png;base64," + data);
    
    if ($("#keep-measurements").prop('checked')) {
        $("#output_measurement").clone().prop('id', 'output_measurement_' + uniqId() ).prependTo("#output_old");
    }

    localStorage.setItem('measurements', $('#output_old').html());
}

function graph(type, csvData, title) {
    $.ajax({
        url: '/graph',
        type: 'post',
        data: {
            type: type,
            title: title,
            csv: csvData
        },
        headers: { 'x-content-encoding': 'base64' },
        success: function(graph, textStatus, jqXHR) {
            measure_success(graph, textStatus, jqXHR, title, csvData);
        }
    }).fail(function(jqXHR, textStatus, errorThrown) {
        alert("AJAX request 'graph' failed: " + textStatus + "\n" + errorThrown);
    })
}

function measure_csv(url, type, steps, freq1, freq2, amp1, amp2, title) {
    $("#start-measurement").prop("disabled",true);
    $("#measurement-in-progress").show();
    var csv = '';
    return $.ajax({
        url: '/measure',
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
        success: function(csvData, textStatus, jqXHR) {
            csv = csvData;
        },
    }).fail(function(jqXHR, textStatus, errorThrown) {
        alert("AJAX request 'measure_csv' failed: " + textStatus + "\n" + errorThrown);
    }).then(function() {
        graph(type, csv, title);
    }).always(function() {
        $("#start-measurement").prop("disabled", false);
        $("#measurement-in-progress").hide();
    })
}

function measure(url, type, steps, freq1, freq2, amp1, amp2, title) {

    return $.ajax({
        url: '/measure_and_graph',
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
        success: function(data, textStatus, jqXHR) {
            measure_success(data, textStatus, jqXHR, title);
        }
    }).fail(function(jqXHR, textStatus, errorThrown) {
        alert("AJAX request failed: " + textStatus + "\n" + errorThrown);
    })
}

function submit_measure(form, event) {
    // Stop form from submitting normally
    event.preventDefault();

    $("#start-measurement").prop("disabled",true);
    $("#measurement-in-progress").show();

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

    if (type.startsWith("MULTI_")) {
        if (type == "MULTI_FR_THD_LVL") {
            measure_csv(url, "LVL_FRQ", freq_steps, freq1, freq2, amp, amp2, title + " (Freq. Resp.)").then(
            measure_csv(url, "THDLV_LVL", amp_steps, freq, freq2, amp1, amp2, title + " (Clipping Behaviour)")).then(
            measure_csv(url, "THDLV_FRQ", freq_steps, freq1, freq2, amp, amp2, title + " (THD+N)"));
        } else if (type == "MULTI_FR_THD") {
            measure_csv(url, "LVL_FRQ", freq_steps, freq1, freq2, amp, amp2, title + " (Freq. Resp.)").then(
            measure_csv(url, "THDLV_FRQ", freq_steps, freq1, freq2, amp, amp2, title + " (THD+N)"));
        }
    } else {
        if (type.endsWith("_LVL")) {
            freq1 = freq;
            // freq2 is ignored in implementation
            steps = amp_steps;
        } else if (type.endsWith("_FRQ")) {
            amp1 = amp;
            // amp2 is ignored in implementation
            steps = freq_steps;
        }

        measure_csv(url, type, steps, freq1, freq2, amp1, amp2, title);
    }   

    $("#start-measurement").prop("disabled", false);
    $("#measurement-in-progress").hide();
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
    if (measurement.startsWith("MULTI_")) {
        $(".amp-static").show();
        $(".amp-sweep").show();

        $(".freq-static").show();
        $(".freq-sweep").show();
    } else if (measurement.endsWith("_FRQ")) {
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
    } 
}

function inject_download() {
    var csvContent = $(this).siblings('.csv_content').text();
    var data = new Blob([csvContent], {type: 'text/csv'});
    var url = window.URL.createObjectURL(data);
    $(this).attr("href", url);
}

function init_downloads() {
    $(".download_csv_link").mousedown(inject_download);
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

    init_downloads();

}