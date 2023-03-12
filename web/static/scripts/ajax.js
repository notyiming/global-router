var netlist_count = 0;
var result_list = [];

$(document).ready(function () {

    $('#netlist-input-form').on('submit', function (e) {
        var netlist_input_data = new FormData($('#netlist-input-form')[0]);
        var netlist_name = $('#inputFile')[0].files[0].name;
        var curr_count = ++netlist_count;
        update_job_monitor(netlist_name, curr_count);
        $.ajax({
            data: netlist_input_data,
            type: 'POST',
            url: '/dashboard',
            contentType: false,
            cache: false,
            processData: false,
            async: true,
            success: function (result) {
                ready_job_state(curr_count);
            }
        })
        e.preventDefault();
    });

    $('#sample-netlist').on('click', function (e) {
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
        var curr_count = ++netlist_count;
        update_job_monitor(sample_netlist_file, curr_count);
        $.ajax({
            data: 'testcase/' + sample_netlist_file,
            type: 'POST',
            url: '/dashboard',
            contentType: false,
            success: function (result) {
                ready_job_state(curr_count);
                result_list.push({sample_netlist_file, result});
            }
        })
        e.preventDefault();
    });

    $('#sample-netlist-select').change(function () {
        $('#sample-netlist').removeAttr('disabled');
    })
});

function ready_job_state(id) {
    $("#netlist-" + id).find("td button").removeAttr("disabled");
    $("#netlist-" + id + " .routing-status").text("Ready").css("color", "green");
}

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

function view_visual(id) {
    netlist = result_list[id-1]
    netlist_name = netlist.sample_netlist_file;
    netlist_data = netlist.result;
    plot_id = add_tab(netlist_data["fig_html"]);
    update_view(netlist_name, netlist_data, plot_id);

}

function update_job_monitor(netlist_name, netlist_count) {
    var jobMonitor = $('#job-monitor');
    var newRowId = "netlist-" + netlist_count;
    var newRow = '<tr id=' + newRowId + '><th scope="row">' + netlist_count + '</th>'
    newRow += ('<td>' + netlist_name + '</td>');
    newRow += ('<td class="routing-status">' + 'Routing' + '</td>');
    newRow += ('<td><button class="btn btn-primary" onclick="view_visual(' + netlist_count + ')" disabled>View</button></td>');
    jobMonitor.append(newRow);
}

function add_tab(fig_html) {
    var numTabs = $('#netlist-tabs li').length;
    var newTabId = 'tab-' + numTabs;
    var newTabContentHtml = '<div class="tab-pane fade" id="' + newTabId + '" role="tabpanel" aria-labelledby="' + newTabId + '-tab">' + '<div class="row"><div id="plot-view" class="col-xl-8">' + fig_html + '</div>' + '<div class="col-xl-4 " id="netlist-output-details">' + '<span><h5>Netlist Details</h5><ul id="netlist-details-list"><li id="netlist-name-' + numTabs + '"></li><li id="grid-size-' + numTabs + '"></li><li id="horcap-' + numTabs + '"></li><li id="vercap-' + numTabs + '"></li><li id="netlist-size-' + numTabs + '"></li><li id="overflow-' + numTabs + '"></li><li id="wirelength-' + numTabs + '"></li></ul></span></div></div>';
    var newTabHtml = '<li class="nav-item" role="presentation"><button class="nav-link" id="' + newTabId + '-tab" data-bs-toggle="pill" data-bs-target="#' + newTabId + '" type="button" role="tab" aria-controls="' + newTabId + '" aria-selected="false">Plot-' + numTabs + '</button></li>';
    if (numTabs === 0) {
        var netlistTabsUL = '<ul class="nav nav-pills mb-3" id="netlist-tabs" role="tablist"></ul>'
        netlistTabsUL += '<div class="tab-content" id="netlist-tabs-content"></div>';
        $('#output-view').removeClass('row');
        $('#output-view').html(netlistTabsUL);
        $('#netlist-tabs').append(newTabHtml);
        $('#netlist-tabs-content').append(newTabContentHtml);
        $('#' + newTabId).addClass('show active');
        $('#' + newTabId + '-tab').addClass('active');
    } else {
        $('#netlist-tabs').append(newTabHtml);
        $('#netlist-tabs-content').append(newTabContentHtml);
    }
    return numTabs;
}