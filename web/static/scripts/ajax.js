$(document).ready(function () {
    $('#netlist-input-form').on('submit', function (e) {
        $('#layout-details-list').attr('hidden', 'true');
        $('#congestion-plot').attr("alt", "Generating Congestion Plot...").attr("src", "");
        $('#submit-netlist')
            .attr("disabled", "true")
            .html("<span class='spinner-border spinner-border-sm' role='status' aria-hidden='true'></span> Processing...");
        var netlist_input_data = new FormData($('#netlist-input-form')[0]);
        $.ajax({
            data: netlist_input_data,
            type: 'POST',
            url: '/dashboard',
            contentType: false,
            cache: false,
            processData: false,
            async: true,
            success: function (result) {
                update_view(result);
                $('#submit-netlist').removeAttr("disabled").html("Submit Netlist");
            }
        })
        e.preventDefault();
    });

    $('#sample-netlist').on('click', function (e) {
        $('#layout-details-list').attr('hidden', 'true');
        $('#congestion-plot').attr("alt", "Generating Congestion Plot...").attr("src", "");
        $('#sample-netlist')
            .attr("disabled", "true")
            .html("<span class='spinner-border spinner-border-sm' role='status' aria-hidden='true'></span> Processing...");
        var selected_netlist = parseInt($('#sample-netlist-select').val());
        let sample_netlist_file;
        switch(selected_netlist) {
            case 1:
                sample_netlist_file = "example.txt";
                break;
            case 2:
                sample_netlist_file = "ibm01.modified.txt";
                break;
            case 3:
                sample_netlist_file = "ibm02.modified.txt";
                break;
            case 4:
                sample_netlist_file = "ibm03.modified.txt";
                break;
            case 5:
                sample_netlist_file = "ibm04.modified.txt";
                break;
            default:
                sample_netlist_file = "example.txt";
                break;
        }
        $.ajax({
            data: 'testcase/' + sample_netlist_file,
            type: 'POST',
            url: '/dashboard',
            contentType: false,
            success: function (result) {
                update_view(result);
                $('#sample-netlist').removeAttr("disabled").html("Use Sample Netlist");
            }
        })
        e.preventDefault();
    });

    $('#sample-netlist-select').change(function(){
        $('#sample-netlist').removeAttr('disabled');
    })
});

function update_view(result) {
    var congestion_plot_img = result["img_src"];
    var ld = result["layout_details"];
    var gridhor = ld["grid_hor"];
    var gridver = ld["grid_ver"];
    var vercap = ld["ver_cap"];
    var horcap = ld["hor_cap"];
    var netlist_size = ld["netlist_size"];
    $('#no-netlist-provided-span').attr("hidden", "true");
    $('#layout-details-list').removeAttr("hidden");
    $('#grid-size').html("Grid: " + gridhor + " x " + gridver);
    $('#horcap').html("Horizontal Capacity: " + horcap);
    $('#vercap').html("Vertical Capacity: " + vercap);
    $('#netlist-size').html("Netlist Size: " + netlist_size);
    $('#congestion-plot').attr("src", congestion_plot_img);
}