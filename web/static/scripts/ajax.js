$(document).ready(function () {
    $('#netlist-input-form').on('submit', function (e) {
        $('#netlist-details-list').attr('hidden', 'true');
        $('#congestion-plot').attr("alt", "Generating Congestion Plot...").attr("src", "");
        $('#submit-netlist')
            .attr("disabled", "true")
            .html("<span class='spinner-border spinner-border-sm' role='status' aria-hidden='true'></span> Processing...");
        $('#no-netlist-provided-span')
        .removeAttr('hidden')
        .html("<span class='spinner-border spinner-border-sm' role='status' aria-hidden='true'></span> Processing Netlist");
        var netlist_input_data = new FormData($('#netlist-input-form')[0]);
        var netlist_name = $('#inputFile')[0].files[0].name;
        $.ajax({
            data: netlist_input_data,
            type: 'POST',
            url: '/dashboard',
            contentType: false,
            cache: false,
            processData: false,
            async: true,
            success: function (result) {
                update_view(netlist_name, result);
                $('#submit-netlist').removeAttr("disabled").html("Submit Netlist");
            }
        })
        e.preventDefault();
    });

    $('#sample-netlist').on('click', function (e) {
        $('#netlist-details-list').attr('hidden', 'true');
        $('#congestion-plot').attr("alt", "Generating Congestion Plot...").attr("src", "");
        $('#sample-netlist')
            .attr("disabled", "true")
            .html("<span class='spinner-border spinner-border-sm' role='status' aria-hidden='true'></span> Processing...");
        $('#no-netlist-provided-span')
        .removeAttr('hidden')
        .html("<span class='spinner-border spinner-border-sm' role='status' aria-hidden='true'></span> Processing Netlist");
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
                update_view(sample_netlist_file, result);
                $('#sample-netlist').removeAttr("disabled").html("Select Netlist");
            }
        })
        e.preventDefault();
    });

    $('#sample-netlist-select').change(function(){
        $('#sample-netlist').removeAttr('disabled');
    })
});

function update_view(netlist_name, result) {
    var congestion_plot_fig_html= result["fig_html"];
    var ld = result["netlist_details"];
    var gridhor = ld["grid_hor"];
    var gridver = ld["grid_ver"];
    var vercap = ld["ver_cap"];
    var horcap = ld["hor_cap"];
    var netlist_size = ld["netlist_size"];
    var overflow = result["overflow"];
    var wirelength = result["wirelength"];
    $('#no-netlist-provided-span').attr("hidden", "true");
    $('#netlist-details-list').removeAttr("hidden");
    $('#netlist-name').html("Name: <b>" + netlist_name + "</b>");
    $('#grid-size').html("Grid: " + gridhor + " x " + gridver);
    $('#horcap').html("Horizontal Capacity: " + horcap);
    $('#vercap').html("Vertical Capacity: " + vercap);
    $('#netlist-size').html("Netlist Size: " + netlist_size);
    $('#overflow').html("Overflow: " + overflow);
    $('#wirelength').html("Wirelength: " + wirelength);
    $('#plot-fig').html(congestion_plot_fig_html);
    $('#plot-1').css({"text-align": "center"});
}