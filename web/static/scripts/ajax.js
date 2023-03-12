$(document).ready(function () {
    $('#netlist-input-form').on('submit', function (e) {
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
                $('#submit-netlist').removeAttr("disabled").html("Submit Netlist");
                id = add_tab(result["fig_html"]);
                update_view(netlist_name, result, id);
            }
        })
        e.preventDefault();
    });

    $('#sample-netlist').on('click', function (e) {
        $('#congestion-plot').attr("alt", "Generating Congestion Plot...").attr("src", "");
        $('#sample-netlist')
            .attr("disabled", "true")
            .html("<span class='spinner-border spinner-border-sm' role='status' aria-hidden='true'></span> Processing...");
        $('#no-netlist-provided-span')
            .removeAttr('hidden')
            .html("<span class='spinner-border spinner-border-sm' role='status' aria-hidden='true'></span> Processing Netlist");
        var selected_netlist = parseInt($('#sample-netlist-select').val());
        let sample_netlist_file;
        switch (selected_netlist) {
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
                $('#sample-netlist').removeAttr("disabled").html("Select Netlist");
                id = add_tab(result["fig_html"]);
                update_view(sample_netlist_file, result, id);
            }
        })
        e.preventDefault();
    });

    $('#sample-netlist-select').change(function () {
        $('#sample-netlist').removeAttr('disabled');
    })
});

function update_view(netlist_name, result, id) {
    var ld = result["netlist_details"];
    var gridhor = ld["grid_hor"];
    var gridver = ld["grid_ver"];
    var vercap = ld["ver_cap"];
    var horcap = ld["hor_cap"];
    var netlist_size = ld["netlist_size"];
    var overflow = result["overflow"];
    var wirelength = result["wirelength"];
    $('#no-netlist-provided-span').attr("hidden", "true");
    $('#netlist-name-' + id).html("Name: " + netlist_name);
    $('#grid-size-' + id).html("Grid: " + gridhor + " x " + gridver);
    $('#horcap-' + id).html("Horizontal Capacity: " + horcap);
    $('#vercap-' + id).html("Vertical Capacity: " + vercap);
    $('#netlist-size-' + id).html("Netlist Size: " + netlist_size);
    $('#overflow-' + id).html("Overflow: " + overflow);
    $('#wirelength-' + id).html("Wirelength: " + wirelength);
}

function add_tab(fig_html) {
    var numTabs = $('#netlist-tabs li').length;
    var newTabId = 'tab-' + numTabs;
    if (numTabs === 0) {
        var netlistTabsUL = '<ul class="nav nav-pills mb-3" id="netlist-tabs" role="tablist"></ul><div class="tab-content" id="netlist-tabs-content"></div>';
        var newTabContentHtml = '<div class="tab-pane fade show active" id="' + newTabId + '" role="tabpanel" aria-labelledby="' + newTabId + '-tab">' + '<div class="card-body row" id="output-view"><div id="plot-view" class="col-xl-8">' + fig_html + '</div>' + '<div class="col-xl-4 " id="netlist-output-details">' + '<span><h5>Netlist Details</h5><ul id="netlist-details-list"><li id="netlist-name-' + numTabs + '"></li><li id="grid-size-' + numTabs + '"></li><li id="horcap-' + numTabs + '"></li><li id="vercap-' + numTabs + '"></li><li id="netlist-size-' + numTabs + '"></li><li id="overflow-' + numTabs + '"></li><li id="wirelength-' + numTabs + '"></li></ul></span></div></div>';
        var newTabHtml = '<li class="nav-item" role="presentation"><button class="nav-link active" id="' + newTabId + '-tab" data-bs-toggle="pill" data-bs-target="#' + newTabId + '" type="button" role="tab" aria-controls="' + newTabId + '" aria-selected="true">New Tab</button></li>';
        $('#output-view').html(netlistTabsUL);
    } else {
        var newTabContentHtml = '<div class="tab-pane fade" id="' + newTabId + '" role="tabpanel" aria-labelledby="' + newTabId + '-tab">' + fig_html + '</div>';
        var newTabContentHtml = '<div class="tab-pane fade" id="' + newTabId + '" role="tabpanel" aria-labelledby="' + newTabId + '-tab">' + '<div class="card-body row" id="output-view"><div id="plot-view" class="col-xl-8">' + fig_html + '</div>' + '<div class="col-xl-4 " id="netlist-output-details">' + '<span><h5>Netlist Details</h5><ul id="netlist-details-list"><li id="netlist-name-' + numTabs + '"></li><li id="grid-size-' + numTabs + '"></li><li id="horcap-' + numTabs + '"></li><li id="vercap-' + numTabs + '"></li><li id="netlist-size-' + numTabs + '"></li><li id="overflow-' + numTabs + '"></li><li id="wirelength-' + numTabs + '"></li></ul></span></div></div>';
        var newTabHtml = '<li class="nav-item" role="presentation"><button class="nav-link" id="' + newTabId + '-tab" data-bs-toggle="pill" data-bs-target="#' + newTabId + '" type="button" role="tab" aria-controls="' + newTabId + '" aria-selected="false">New Tab</button></li>';
    }
    $('#netlist-tabs').append(newTabHtml);
    $('#netlist-tabs-content').append(newTabContentHtml);
    return numTabs;
}