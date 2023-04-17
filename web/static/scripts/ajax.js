var result_cache_list = [];
var netlist_count = $("#netlist-tabs li").length;

$(document).ready(function () {
  $("#inputFileOption").click(function () {
    $("#inputFile").prop("disabled", false);
    $("#sample-netlist-select")
      .prop("disabled", true)
      .val("Select a sample netlist");
    $("#submit-netlist").prop("disabled", true);
  });

  $("#sampleFileOption").click(function () {
    $("#sample-netlist-select").prop("disabled", false);
    $("#inputFile").prop("disabled", true).val("");
    $("#submit-netlist").prop("disabled", true);
  });

  $("#netlist-input-form").on("submit", function (e) {
    e.preventDefault();
    var netlist_input_data = new FormData();
    let netlist_name;
    if ($("#inputFile")[0].files.length > 0) {
      netlist_name = $("#inputFile")[0].files[0].name;
      netlist_input_data.append("input-file", $("#inputFile")[0].files[0]);
    } else {
      let selected_netlist = parseInt($("#sample-netlist-select").val());
      netlist_name = [
        "example",
        "ibm01.modified",
        "ibm02.modified",
        "ibm03.modified",
        "ibm04.modified",
      ][selected_netlist - 1];
      netlist_path = "testcase/" + netlist_name + ".txt";
      netlist_input_data.append("sample-netlist-select", netlist_path);
    }

    var curr_count = ++netlist_count;
    update_job_monitor(netlist_name, curr_count);
    netlist_input_data.append("algorithm-select", $("#algorithm-select").val());
    netlist_input_data.append("seed-input", $("#seed-input").val());

    $.ajax({
      data: netlist_input_data,
      type: "POST",
      url: "/dashboard",
      contentType: false,
      cache: false,
      processData: false,
      async: true,
      success: function (result) {
        ready_job_state(curr_count, result["timestamp"]);
        result_cache_list.push({ netlist_name, result });
      },
    });
  });

  $("#sample-netlist-select, #inputFile").change(function () {
    $("#submit-netlist").removeAttr("disabled");
  });
});

function ready_job_state(id, timestamp) {
  $("#netlist-" + id)
    .find("td button")
    .removeAttr("disabled");
  $("#netlist-" + id + " .routing-status")
    .text("Ready")
    .css("color", "green");
  $("#netlist-" + id + "-timestamp").text(timestamp);
}

function update_view(netlist_name, result, id) {
  var ld = result["netlist_details"];
  $("#no-netlist-provided-span").attr("hidden", "true");
  $("#netlist-name-" + id).html("Name: " + netlist_name);
  $("#grid-size-" + id).html("Grid: " + ld.grid_hor + " x " + ld.grid_ver);
  $("#horcap-" + id).html("Horizontal Capacity: " + ld.hor_cap);
  $("#vercap-" + id).html("Vertical Capacity: " + ld.ver_cap);
  $("#netlist-size-" + id).html("Netlist Size: " + ld.netlist_size);
  $("#overflow-" + id).html("Overflow: " + result.overflow);
  $("#wirelength-" + id).html("Wirelength: " + result.wirelength);
  $("#timestamp-" + id).html("Timestamp: " + result.timestamp);
  $("#algorithm-" + id).html("Algorithm: " + result.algorithm);
  $("#seed-" + id).html("Seed: " + result.seed);
  $("#download-output-" + id).attr("href", "download/" + result.unique_name);
}

function view_visual(id) {
  netlist = result_cache_list[id];
  netlist_name = netlist.netlist_name;
  netlist_data = netlist.result;
  $("#netlist-" + netlist_count)
    .find("td button")
    .attr("disabled", "disabled")
    .text("Opened");
  add_tab(netlist_data["fig_html"], netlist_count);
  update_view(netlist_name, netlist_data, netlist_count);
}

function update_job_monitor(netlist_name, netlist_count) {
  var jobMonitor = $("#job-monitor");
  var newRowId = "netlist-" + netlist_count;
  var newRow =
    "<tr id=" + newRowId + '><th scope="row">' + netlist_count + "</th>";
  newRow += "<td>" + netlist_name + "</td>";
  newRow += '<td class="routing-status">' + "Routing" + "</td>";
  newRow += "<td id =" + newRowId + "-timestamp" + "> - </td>";
  newRow +=
    '<td><button class="btn btn-primary" onclick="view_visual(' +
    result_cache_list.length +
    ')" disabled>View</button></td>';
  jobMonitor.append(newRow);
}

function add_tab(figHtml, id) {
  var numTabs = id;
  const newTabId = `tab-${numTabs}`;
  const newTabContentHtml = `
    <div class="tab-pane fade" id="${newTabId}" role="tabpanel" aria-labelledby="${newTabId}-tab">
      <div class="row">
        <div id="plot-view" class="col-xl-8">${figHtml}</div>
        <div class="col-xl-4" id="netlist-output-details">
          <span>
            <h5>Netlist Details</h5>
            <ul id="netlist-details-list">
              <li id="netlist-name-${numTabs}"></li>
              <li id="grid-size-${numTabs}"></li>
              <li id="horcap-${numTabs}"></li>
              <li id="vercap-${numTabs}"></li>
              <li id="netlist-size-${numTabs}"></li>
              <li id="overflow-${numTabs}"></li>
              <li id="wirelength-${numTabs}"></li>
              <li id="timestamp-${numTabs}"></li>
              <li id="algorithm-${numTabs}"></li>
              <li id="seed-${numTabs}"></li>
            </ul>
            <a href="#" id="download-output-${numTabs}" class="btn btn-primary">Download Output</a>
          </span>
        </div>
      </div>
    </div>`;
  const newTabHtml = `
    <li class="nav-item" role="presentation">
      <button class="nav-link" id="${newTabId}-tab" data-bs-toggle="pill" data-bs-target="#${newTabId}" type="button" role="tab" aria-controls="${newTabId}" aria-selected="false">Plot-${numTabs}</button>
    </li>`;
  if (numTabs === 1) {
    const netlistTabsUL = `
      <ul class="nav nav-pills mb-3" id="netlist-tabs" role="tablist"></ul>
      <div class="tab-content" id="netlist-tabs-content"></div>`;
    $("#output-view").removeClass("row");
    $("#output-view").html(netlistTabsUL);
    $("#netlist-tabs").append(newTabHtml);
    $("#netlist-tabs-content").append(newTabContentHtml);
    $("#" + newTabId).addClass("show active");
    $("#" + newTabId + "-tab").addClass("active");
  } else {
    $("#netlist-tabs").append(newTabHtml);
    $("#netlist-tabs-content").append(newTabContentHtml);
  }
}
