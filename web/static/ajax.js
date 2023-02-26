$(document).ready(function () {
    $('#netlist-input-form').on('submit', function (e) {
        console.log("here");
        $('#congestion-plot').attr("alt", "loading...").attr("src", "");
        var netlist_input_data = new FormData($('#netlist-input-form')[0]);
        $.ajax({
            data: netlist_input_data,
            type: 'POST',
            url: '/dashboard',
            contentType: false,
            cache: false,
            processData: false,
            success: function (result) {
                $('#congestion-plot').attr("src", result);
            }
        })
        e.preventDefault();
    });

    $('#sample-netlist').on('click', function (e) {
        $('#congestion-plot').attr("alt", "loading...").attr("src", "");
        var data = {"sample_netlist_file_path": "testcase/example.txt"}
        $.ajax({
            data: JSON.stringify(data),
            type: 'POST',
            url: '/dashboard',
            contentType: "application/json",
            dataType: "json",

            // cache: false,
            // processData: false,
            success: function (result) {
                console.log("hello?");
                $('#congestion-plot').attr("src", result);
            }
        })
        e.preventDefault();
    });
});