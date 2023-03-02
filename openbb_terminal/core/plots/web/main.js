let globals = { dark_mode: false, modebarHidden: false };

TITLE_DIV = undefined;
TEXT_DIV = undefined;
CSV_DIV = undefined;
CHART_DIV = undefined;

let check_divs = setInterval(function () {
  // Wait for the popup divs to be loaded before assigning them to variables
  let div_ids = ["popup_title", "popup_text", "popup_csv", "openbb_chart"];
  let divs = div_ids.map(function (id) {
    return document.getElementById(id);
  });

  if (
    divs.every(function (div) {
      return div != null;
    })
  ) {
    TITLE_DIV = document.getElementById("popup_title");
    TEXT_DIV = document.getElementById("popup_text");
    CSV_DIV = document.getElementById("popup_csv");
    CHART_DIV = document.getElementById("openbb_chart");
    console.log("popup divs found");
    clearInterval(check_divs);
  }
}, 100);

function OpenBBMain(plotly_figure) {
  // Main function that plots the graphs and initializes the bar menus
  globals.chartDiv = CHART_DIV;
  console.log("main.js loaded");
  console.log("plotly_figure", plotly_figure);
  let graphs = plotly_figure;

  // Sets the config with the custom buttons
  CONFIG = {
    scrollZoom: true,
    responsive: true,
    displaylogo: false,
    displayModeBar: true,
    toImageButtonOptions: {
      format: "svg",
      filename: openbbFilename(graphs),
      height: CHART_DIV.clientHeight,
      width: CHART_DIV.clientWidth,
    },
    modeBarButtonsToRemove: ["lasso2d", "select2d"],
    modeBarButtons: [
      [
        {
          name: "Download Data (Ctrl+S)",
          icon: Plotly.Icons.disk,
          click: function (gd) {
            downloadData(gd);
          },
        },
        {
          name: "Upload Image (Ctrl+U)",
          icon: Plotly.Icons.uploadImage,
          click: function (gd) {
            downloadImage();
          },
        },
        "toImage",
      ],
      ["drawline", "drawopenpath", "drawcircle", "drawrect", "eraseshape"],
      ["zoomIn2d", "zoomOut2d", "resetScale2d", "zoom2d", "pan2d"],
      [
        {
          name: "Add Text (Ctrl+T)",
          icon: ICONS.addText,
          click: function () {
            openPopup("popup_text");
          },
        },
        {
          name: "Change Titles (Ctrl+Shift+T)",
          icon: ICONS.changeTitle,
          click: function () {
            openPopup("popup_title");
          },
        },
        {
          name: "Plot CSV (Ctrl+Shift+C)",
          icon: ICONS.plotCsv,
          click: function () {
            // We make sure to close any other popup that might be open
            // before opening the CSV popup
            closePopup();
            openPopup("popup_csv");
          },
        },
        {
          name: "Edit Color (Ctrl+E)",
          icon: ICONS.changeColor,
          click: function () {
            // We need to check if the button is active or not
            let title = "Edit Color (Ctrl+E)";
            let button = globals.barButtons[title];
            let active = true;
            if (button.style.border == "transparent") {
              active = false;
            }
            // We call the function that changes the border color
            button_pressed(title, active);
            changeColor();
          },
        },
        {
          name: "Auto Scale (Ctrl+Shift+A)",
          icon: Plotly.Icons.autoscale,
          click: function () {
            // We need to check if the button is active or not
            let title = "Auto Scale (Ctrl+Shift+A)";
            let button = globals.barButtons[title];
            let active = true;
            if (button.style.border == "transparent") {
              active = false;
              // We add the listener to the plotly_relayout event
              // to autoscale the graphs
              CHART_DIV.on("plotly_relayout", function (eventdata) {
                autoScaling(eventdata, graphs);
              });
            } else {
              // If the button is active, we remove the listener so
              // the graphs don't autoscale anymore
              CHART_DIV.removeAllListeners("plotly_relayout");
            }
            button_pressed(title, active);
          },
        },
        "hoverClosestCartesian",
        "hoverCompareCartesian",
        "toggleSpikelines",
      ],
    ],
  };

  // We make sure to fill in any missing layout properties with default values
  if (!("font" in graphs.layout)) {
    graphs.layout["font"] = {
      family: "Fira Code, monospace, Arial Black",
      size: 18,
    };
  }
  graphs.layout.annotations = !graphs.layout.annotations
    ? []
    : graphs.layout.annotations;

  if (!("margin" in graphs.layout)) {
    graphs.layout["margin"] = {
      l: 0,
      r: 0,
      b: 0,
      t: 0,
      pad: 2,
    };
  }

  // We setup keyboard shortcuts custom to OpenBB
  window.document.addEventListener("keydown", function (e) {
    if (e.ctrlKey && e.key.toLowerCase() == "t") {
      openPopup("popup_text");
    }
    if (e.ctrlKey && e.key.toLowerCase() == "e") {
      changeColor();
    }
    if (e.ctrlKey && e.shiftKey && e.key.toLowerCase() == "t") {
      openPopup("popup_title");
    }
    if (e.ctrlKey && e.key.toLowerCase() == "s") {
      downloadData(CHART_DIV);
    }
    if (e.ctrlKey && e.shiftKey && e.key.toLowerCase() == "c") {
      openPopup("popup_csv");
    }
    if (e.key == "Escape") {
      closePopup();
    }
  });

  graphs.layout.autosize = true;
  // We set the height and width to undefined, so that plotly.js can
  // automatically resize the chart to fit the PyWry window
  delete graphs.layout.height;
  delete graphs.layout.width;

  if (graphs.layout.annotations != undefined) {
    graphs.layout.annotations.forEach(function (annotation) {
      // We make sure to fill in any missing annotation properties with default values
      // We also make sure to set the font size to a reasonable value based on the
      // width of the client window
      if (!("font" in annotation) || !("size" in annotation.font)) {
        annotation["font"] = {
          family: "Fira Code, monospace, Arial Black",
          size: 16,
        };
      }

      annotation.font.size = Math.min(
        CHART_DIV.clientWidth / 50,
        annotation.font.size
      );
    });
  }

  // We add spaces to all trace names, due to Fira Code font width issues
  // to make sure that the legend is not cut off
  graphs.data.forEach(function (trace) {
    if (trace.name != undefined) {
      trace.name = trace.name + "     ";
    }
  });

  // Set the default dragmode to pan and set the font size to a reasonable value
  graphs.layout.dragmode = "pan";
  graphs.layout.font.size = Math.min(
    CHART_DIV.clientWidth / 50,
    graphs.layout.font.size
  );

  // We check for the dark mode
  if (graphs.layout.template.layout.mapbox.style == "dark") {
    document.body.style.backgroundColor = "#000000";
    graphs.layout.template.layout.paper_bgcolor = "#000000";
    graphs.layout.template.layout.plot_bgcolor = "#000000";
  }

  // We set the plot config and plot the chart
  Plotly.setPlotConfig(CONFIG);
  Plotly.newPlot(CHART_DIV, graphs, { responsive: true });

  // Create global variables to for use later
  let modebar = document.getElementsByClassName("modebar-container");
  let modebar_buttons = modebar[0].getElementsByClassName("modebar-btn");
  globals.barButtons = {};

  for (let i = 0; i < modebar_buttons.length; i++) {
    // We add the buttons to the global variable for later use
    // and set the border to transparent so we can change the
    // color of the buttons when they are pressed
    let button = modebar_buttons[i];
    button.style.border = "transparent";
    globals.barButtons[button.getAttribute("data-title")] = button;
  }

  // We check if the chart is a 3D mesh to make sure to adjust the
  // window close interval if exporting plot to image
  let is_3dmesh = false;

  // We add a listener to the chart div to listen for relayout events
  // we only care about the yaxis.type event
  CHART_DIV.on("plotly_relayout", function (eventdata) {
    if (CHART_DIV.layout.yaxis.type != undefined) {
      if (
        eventdata["yaxis.type"] == "log" ||
        (CHART_DIV.layout.yaxis.type == "log" && !globals.logYaxis)
      ) {
        console.log("yaxis.type changed to log");
        globals.logYaxis = true;

        // We update the yaxis exponent format to SI,
        // set the tickformat to '.0s' and the exponentbase to 100
        Plotly.relayout(CHART_DIV, {
          "yaxis.exponentformat": "SI",
          "yaxis.tickformat": ".0s",
          "yaxis.exponentbase": 100,
        });
      }
      if (eventdata["yaxis.type"] == "linear" && globals.logYaxis) {
        console.log("yaxis.type changed to linear");
        globals.logYaxis = false;

        // We update the yaxis exponent format to none,
        // set the tickformat to null and the exponentbase to 10
        Plotly.relayout(CHART_DIV, {
          "yaxis.exponentformat": "none",
          "yaxis.tickformat": null,
          "yaxis.exponentbase": 10,
        });
      }
    } else {
      is_3dmesh = true;
    }

  });

  // send a relayout event to trigger the initial zoom/bars-resize
  // check if the xaxis.range is defined
  if (graphs.layout.xaxis != undefined && graphs.layout.xaxis.range != undefined) {
    Plotly.relayout(CHART_DIV, {
      "xaxis.range[0]": graphs.layout.xaxis.range[0],
      "xaxis.range[1]": graphs.layout.xaxis.range[1],
    });
  }

  // Just in case the CSV_DIV is undefined, we check for it every 100ms
  let check_csv = setInterval(function () {
    if (CSV_DIV != undefined) {
      console.log("CSV_DIV is defined");
      // We add the event listeners for csv file/type changes
      CSV_DIV.querySelector("#csv_file").addEventListener(
        "change",
        function () {
          checkFile(CSV_DIV);
        }
      );
      CSV_DIV.querySelector("#csv_trace_type").addEventListener(
        "change",
        function () {
          console.log("type changed");
          checkFile(CSV_DIV, true);
        }
      );
      clearInterval(check_csv);
    }
  }, 100);

  // We check to see if window.save_png is defined and true
  if (window.save_image != undefined && window.export_image) {
    // if is_3dmesh is true, we set the close_interval to 1000
    let close_interval = is_3dmesh ? 1000 : 500;

    // We get the extension of the file and check if it is valid
    const extension = window.export_image.split(".").pop().replace("jpg", "jpeg");

    if (["jpeg", "png", "svg"].includes(extension)) {
      // We run Plotly.downloadImage to save the chart as an image
      Plotly.downloadImage(CHART_DIV, {
        format: extension,
        width: CHART_DIV.clientWidth,
        height: CHART_DIV.clientHeight,
        filename: window.export_image.split("/").pop(),
      });

    }
    setTimeout(function () {
      window.close();
    }, close_interval);
  }
}

// listen to cmd+h or ctrl+h to hide the modebar
document.addEventListener("keydown", function (event) {
  if (event.key == "h" && (event.ctrlKey || event.metaKey)) {
    event.preventDefault();
    const modebar = document.getElementsByClassName("modebar-container")[0];
    if (globals.modebarHidden) {
      modebar.style.display = "flex";
      globals.modebarHidden = false;
    } else {
      modebar.style.display = "none";
      globals.modebarHidden = true;
    }
  }
});
