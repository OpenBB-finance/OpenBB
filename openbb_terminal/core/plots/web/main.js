let globals = {
  dark_mode: false,
  modebarHidden: false,
  added_traces: [],
  csv_yaxis_id: null,
  cmd_src_idx: null,
};

function loadingOverlay(message) {
  const loading = document.getElementById("loading");
  const loading_text = document.getElementById("loading_text");

  loading_text.innerHTML = message;
  loading.classList.add("show");

  let is_loaded = setInterval(function () {
    if (loading.classList.contains("show")) {
      clearInterval(is_loaded);
    }
  }, 10);
}

const non_blocking = (func, delay) => {
  let timeout;
  return function () {
    const context = this;
    const args = arguments;
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(context, args), delay);
  };
};

function OpenBBMain(plotly_figure, chartdiv, csvdiv, textdiv, titlediv) {
  // Main function that plots the graphs and initializes the bar menus
  globals.CHART_DIV = chartdiv;
  globals.TITLE_DIV = titlediv;
  globals.TEXT_DIV = textdiv;
  globals.CSV_DIV = csvdiv;
  console.log("main.js loaded");
  console.log("plotly_figure", plotly_figure);
  let graphs = plotly_figure;

  const loading = document.getElementById("loading");

  // We add the event listeners for csv file/type changes
  globals.CSV_DIV.querySelector("#csv_file").addEventListener(
    "change",
    function () {
      console.log("file changed");
      loadingOverlay("Loading CSV");
      setTimeout(function () {
        non_blocking(function () {
          checkFile(globals.CSV_DIV);
        }, 2)();
        setTimeout(function () {
          loading.classList.remove("show");
        }, 200);
      }, 1000);
    }
  );
  globals.CSV_DIV.querySelector("#csv_trace_type").addEventListener(
    "change",
    function () {
      console.log("type changed");
      checkFile(globals.CSV_DIV, true);
    }
  );

  globals.filename = openbbFilename(graphs);

  // Sets the config with the custom buttons
  CONFIG = {
    scrollZoom: true,
    responsive: true,
    displaylogo: false,
    displayModeBar: true,
    modeBarButtonsToRemove: ["lasso2d", "select2d", "downloadImage"],
    modeBarButtons: [
      [
        {
          name: "Download Data (Ctrl+S)",
          icon: Plotly.Icons.disk,
          click: function (gd) {
            loadingOverlay("Saving CSV");
            setTimeout(function () {
              downloadData(gd);
            }, 500);
            setTimeout(function () {
              loading.classList.remove("show");
            }, 1000);
          },
        },
        // {
        //   name: "Upload Image (Ctrl+U)",
        //   icon: Plotly.Icons.uploadImage,
        //   click: function (gd) {
        //     downloadImage();
        //   },
        // },
        {
          name: "Download Plot",
          icon: Plotly.Icons.camera,
          click: function () {
            loadingOverlay("Saving Image");
            hideModebar();
            non_blocking(function () {
              downloadImage(globals.filename, "png");
              setTimeout(function () {
                setTimeout(function () {
                  loading.classList.remove("show");
                  hideModebar();
                }, 50);
              }, 25);
            }, 2)();
          },
        },
      ],
      [
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
        "drawline",
        "drawopenpath",
        "drawcircle",
        "drawrect",
        "eraseshape",
      ],
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
          name: "Auto Scale (Ctrl+Shift+A)",
          icon: Plotly.Icons.autoscale,
          click: function () {
            // We need to check if the button is active or not
            let title = "Auto Scale (Ctrl+Shift+A)";
            let button = globals.barButtons[title];
            let active = true;
            if (button.style.border == "transparent") {
              active = false;
              globals.CHART_DIV.on(
                "plotly_relayout",
                non_blocking(function (eventdata) {
                  if (eventdata["xaxis.range[0]"] == undefined) {
                    return;
                  }
                  autoScaling(eventdata, globals.CHART_DIV);
                }, 100)
              );
            } else {
              // If the button isn't active, we remove the listener so
              // the graphs don't autoscale anymore
              globals.CHART_DIV.removeAllListeners("plotly_relayout");
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
  graphs.layout.title = "";

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

      if (annotation.text != undefined) {
        if (annotation.text[0] == "/") {
          globals.cmd_src_idx = graphs.layout.annotations.indexOf(annotation);
        }
      }
      annotation.font.size = Math.min(
        globals.CHART_DIV.clientWidth / 50,
        annotation.font.size
      );
    });
  }

  // We add spaces to all trace names, due to Fira Code font width issues
  // to make sure that the legend is not cut off
  graphs.data.forEach(function (trace) {
    if (trace.name != undefined) {
      let name_length = trace.name.length;
      trace.name = trace.name + "         ";
      trace.hoverlabel = {
        namelength: name_length,
      };
    }
  });

  // Set the default dragmode to pan and set the font size to a reasonable value
  graphs.layout.dragmode = "pan";
  graphs.layout.font.size = Math.min(
    globals.CHART_DIV.clientWidth / 50,
    graphs.layout.font.size
  );

  // We check for the dark mode
  if (graphs.layout.template.layout.mapbox.style == "dark") {
    document.body.style.backgroundColor = "#000000";
    document.getElementById("openbb_footer").style.color = "#000000";
    graphs.layout.template.layout.paper_bgcolor = "#000000";
    graphs.layout.template.layout.plot_bgcolor = "#000000";
  } else {
    document.body.style.backgroundColor = "#FFFFFF";
    document.getElementById("openbb_footer").style.color = "#FFFFFF";
  }

  // We set the plot config and plot the chart
  Plotly.setPlotConfig(CONFIG);
  Plotly.newPlot(globals.CHART_DIV, graphs, { responsive: true });

  // Create global variables to for use later
  const modebar = document.getElementsByClassName("modebar-container")[0];
  const modebar_buttons = modebar.getElementsByClassName("modebar-btn");
  globals.barButtons = {};

  for (let i = 0; i < modebar_buttons.length; i++) {
    // We add the buttons to the global variable for later use
    // and set the border to transparent so we can change the
    // color of the buttons when they are pressed
    let button = modebar_buttons[i];
    button.style.border = "transparent";
    globals.barButtons[button.getAttribute("data-title")] = button;
  }

  if (globals.CHART_DIV.layout.yaxis.type != undefined) {
    if (globals.CHART_DIV.layout.yaxis.type == "log" && !globals.logYaxis) {
      console.log("yaxis.type changed to log");
      globals.logYaxis = true;

      // We update the yaxis exponent format to SI,
      // set the tickformat to '.0s' and the exponentbase to 100
      let layout_update = {
        "yaxis.exponentformat": "SI",
        "yaxis.tickformat": ".0s",
        "yaxis.exponentbase": 100,
      };
      Plotly.update(globals.CHART_DIV, layout_update);
    }
    if (globals.CHART_DIV.layout.yaxis.type == "linear" && globals.logYaxis) {
      console.log("yaxis.type changed to linear");
      globals.logYaxis = false;

      // We update the yaxis exponent format to none,
      // set the tickformat to null and the exponentbase to 10
      let layout_update = {
        "yaxis.exponentformat": "none",
        "yaxis.tickformat": null,
        "yaxis.exponentbase": 10,
      };
      Plotly.update(globals.CHART_DIV, layout_update);
    }
  }

  if (window.plotly_figure.layout.template.layout.mapbox.style === "light") {
    for (const el of document.styleSheets[0].cssRules) {
      if (el.selectorText === ".modebar-group") {
        el.style.backgroundColor = "#FFFFFF";
      }
    }
  }

  function hideModebar() {
    if (globals.modebarHidden) {
      modebar.style.display = "flex";
      globals.modebarHidden = false;
    } else {
      modebar.style.display = "none";
      globals.modebarHidden = true;
    }
  }

  // We setup keyboard shortcuts custom to OpenBB
  window.document.addEventListener("keydown", function (e) {
    if (e.key.toLowerCase() == "h" && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      hideModebar();
    }
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
      downloadData(globals.CHART_DIV);
    }
    if (e.ctrlKey && e.shiftKey && e.key.toLowerCase() == "c") {
      e.preventDefault();
      openPopup("popup_csv");
    }
    if (e.key == "Escape") {
      closePopup();
    }
  });

  // send a relayout event to trigger the initial zoom/bars-resize
  // check if the xaxis.range is defined
  if (
    graphs.layout.xaxis != undefined &&
    graphs.layout.xaxis.range != undefined
  ) {
    Plotly.relayout(globals.CHART_DIV, {
      "xaxis.range[0]": graphs.layout.xaxis.range[0],
      "xaxis.range[1]": graphs.layout.xaxis.range[1],
    });
  }

  // We check to see if window.save_png is defined and true
  if (window.save_image != undefined && window.export_image) {
    // We get the extension of the file and check if it is valid
    let filename = window.export_image.split("/").pop();
    const extension = filename.split(".").pop().replace("jpg", "jpeg");

    if (["jpeg", "png", "svg", "pdf"].includes(extension)) {
      hideModebar();
      non_blocking(function () {
        downloadImage(filename.split(".")[0], extension);
      }, 2)();
    }
  }
}
