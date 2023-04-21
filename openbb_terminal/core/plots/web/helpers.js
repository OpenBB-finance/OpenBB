const ICONS = {
  sunIcon: {
    width: 16,
    height: 16,
    path: "M8 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM8 0a.5.5 0 0 1 .5.5v2a.5.5 0 0 1-1 0v-2A.5.5 0 0 1 8 0zm0 13a.5.5 0 0 1 .5.5v2a.5.5 0 0 1-1 0v-2A.5.5 0 0 1 8 13zm8-5a.5.5 0 0 1-.5.5h-2a.5.5 0 0 1 0-1h2a.5.5 0 0 1 .5.5zM3 8a.5.5 0 0 1-.5.5h-2a.5.5 0 0 1 0-1h2A.5.5 0 0 1 3 8zm10.657-5.657a.5.5 0 0 1 0 .707l-1.414 1.415a.5.5 0 1 1-.707-.708l1.414-1.414a.5.5 0 0 1 .707 0zm-9.193 9.193a.5.5 0 0 1 0 .707L3.05 13.657a.5.5 0 0 1-.707-.707l1.414-1.414a.5.5 0 0 1 .707 0zm9.193 2.121a.5.5 0 0 1-.707 0l-1.414-1.414a.5.5 0 0 1 .707-.707l1.414 1.414a.5.5 0 0 1 0 .707zM4.464 4.465a.5.5 0 0 1-.707 0L2.343 3.05a.5.5 0 1 1 .707-.707l1.414 1.414a.5.5 0 0 1 0 .708z",
  },
  plotCsv: {
    width: 900,
    height: 900,
    path: "M170.666667 106.666667l0.192 736H906.666667v64H149.546667c-23.552 0-42.666667-19.093333-42.666667-42.666667L106.666667 106.666667h64z m686.506666 454.144l13.653334 16.362666a21.333333 21.333333 0 0 1-2.666667 30.058667l-171.157333 143.146667a21.333333 21.333333 0 0 1-21.546667 3.477333l-229.973333-91.285333-113.834667 94.997333a21.333333 21.333333 0 0 1-30.037333-2.709333l-13.653334-16.362667a21.333333 21.333333 0 0 1 2.688-30.058667l133.312-111.274666a21.333333 21.333333 0 0 1 21.546667-3.456l229.930667 91.264 151.68-126.826667a21.333333 21.333333 0 0 1 30.037333 2.666667z m-1.621333-417.962667l16.896 13.013333a21.333333 21.333333 0 0 1 3.925333 29.888L685.802667 433.706667a21.333333 21.333333 0 0 1-20.202667 8.085333l-226.794667-35.413333-150.186666 222.357333a21.333333 21.333333 0 0 1-27.477334 7.018667l-2.133333-1.28-17.685333-11.946667a21.333333 21.333333 0 0 1-5.738667-29.610667l165.354667-244.821333a21.333333 21.333333 0 0 1 20.992-9.130667L650.453333 374.613333l175.146667-227.882666a21.333333 21.333333 0 0 1 29.930667-3.904z",
  },
  addText: {
    path: "M896 928H128a32 32 0 0 1-32-32V128a32 32 0 0 1 32-32h768a32 32 0 0 1 32 32v768a32 32 0 0 1-32 32z m-736-64h704v-704h-704z M704 352H320a32 32 0 0 1 0-64h384a32 32 0 0 1 0 64z M512 736a32 32 0 0 1-32-32V320a32 32 0 0 1 64 0v384a32 32 0 0 1-32 32z",
    width: 950,
    height: 950,
  },
  changeTitle: {
    path: "M122.368 165.888h778.24c-9.216 0-16.384-7.168-16.384-16.384v713.728c0-9.216 7.168-16.384 16.384-16.384h-778.24c9.216 0 16.384 7.168 16.384 16.384V150.016c0 8.192-6.656 15.872-16.384 15.872z m-32.768 684.544c0 26.112 20.992 47.104 47.104 47.104h750.08c26.112 0 47.104-20.992 47.104-47.104V162.304c0-26.112-20.992-47.104-47.104-47.104H136.704c-26.112 0-47.104 20.992-47.104 47.104v688.128z M244.736 656.896h534.016v62.464H244.736z M373.76 358.4H307.2v219.136h-45.568V358.4H192v-41.472H373.76V358.4zM403.968 316.928h44.032v50.176h-44.032v-50.176z m0 67.072h44.032v194.048h-44.032V384zM576.512 541.184l8.704 31.744c-13.312 5.12-26.624 8.192-38.912 8.704-32.768 1.024-48.64-15.36-48.128-48.128V422.912h-26.624V384h26.624v-46.592l44.032-21.504V384h36.352v38.912h-36.352V532.48c-1.024 10.24 3.072 14.848 11.264 13.824 5.12 0 12.8-1.536 23.04-5.12zM619.008 316.928h44.032v260.608h-44.032V316.928zM813.056 509.952l41.472 12.8c-11.776 40.96-37.888 61.44-78.336 60.416-52.736-1.536-80.384-34.304-81.92-98.304 2.56-67.072 29.696-102.4 81.92-105.984 52.224 1.536 78.336 36.864 79.36 105.984v13.824h-117.248c3.584 30.208 15.872 45.568 37.888 46.592 19.968 0.512 32.256-11.264 36.864-35.328z m-72.704-51.712h70.656c-1.024-25.088-12.288-38.4-33.792-38.912-21.504 0.512-33.792 13.824-36.864 38.912z",
    width: 920,
    height: 900,
  },
  changeColor: {
    path: "M8 3C5.79 3 4 4.79 4 7V14C4 15.1 4.9 16 6 16H9V20C9 21.1 9.9 22 11 22H13C14.1 22 15 21.1 15 20V16H18C19.1 16 20 15.1 20 14V3H8M8 5H12V7H14V5H15V9H17V5H18V10H6V7C6 5.9 6.9 5 8 5M6 14V12H18V14H6Z",
    width: 22,
    height: 22,
  },
  uploadImage: {
    path: "M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5",
    width: 1024,
    height: 1024,
  },
  downloadCsv: {
    path: `M486.2,196.121h-13.164V132.59c0-0.399-0.064-0.795-0.116-1.2c-0.021-2.52-0.824-5-2.551-6.96L364.656,3.677
		c-0.031-0.034-0.064-0.044-0.085-0.075c-0.629-0.707-1.364-1.292-2.141-1.796c-0.231-0.157-0.462-0.286-0.704-0.419
		c-0.672-0.365-1.386-0.672-2.121-0.893c-0.199-0.052-0.377-0.134-0.576-0.188C358.229,0.118,357.4,0,356.562,0H96.757
		C84.893,0,75.256,9.649,75.256,21.502v174.613H62.093c-16.972,0-30.733,13.756-30.733,30.73v159.81
		c0,16.966,13.761,30.736,30.733,30.736h13.163V526.79c0,11.854,9.637,21.501,21.501,21.501h354.777
		c11.853,0,21.502-9.647,21.502-21.501V417.392H486.2c16.966,0,30.729-13.764,30.729-30.731v-159.81
		C516.93,209.872,503.166,196.121,486.2,196.121z M96.757,21.502h249.053v110.006c0,5.94,4.818,10.751,10.751,10.751h94.973v53.861
		H96.757V21.502z M258.618,313.18c-26.68-9.291-44.063-24.053-44.063-47.389c0-27.404,22.861-48.368,60.733-48.368
		c18.107,0,31.447,3.811,40.968,8.107l-8.09,29.3c-6.43-3.107-17.862-7.632-33.59-7.632c-15.717,0-23.339,7.149-23.339,15.485
		c0,10.247,9.047,14.769,29.78,22.632c28.341,10.479,41.681,25.239,41.681,47.874c0,26.909-20.721,49.786-64.792,49.786
		c-18.338,0-36.449-4.776-45.497-9.77l7.38-30.016c9.772,5.014,24.775,10.006,40.264,10.006c16.671,0,25.488-6.908,25.488-17.396
		C285.536,325.789,277.909,320.078,258.618,313.18z M69.474,302.692c0-54.781,39.074-85.269,87.654-85.269
		c18.822,0,33.113,3.811,39.549,7.149l-7.392,28.816c-7.38-3.084-17.632-5.939-30.491-5.939c-28.822,0-51.206,17.375-51.206,53.099
		c0,32.158,19.051,52.4,51.456,52.4c10.947,0,23.097-2.378,30.241-5.238l5.483,28.346c-6.672,3.34-21.674,6.919-41.208,6.919
		C98.06,382.976,69.474,348.424,69.474,302.692z M451.534,520.962H96.757v-103.57h354.777V520.962z M427.518,380.583h-42.399
		l-51.45-160.536h39.787l19.526,67.894c5.479,19.046,10.479,37.386,14.299,57.397h0.709c4.048-19.298,9.045-38.352,14.526-56.693
		l20.487-68.598h38.599L427.518,380.583z`,
    width: 550,
    height: 550,
    transform: "translate(4, 0)",
  },
  downloadImage: {
    path: "M22.71,6.29a1,1,0,0,0-1.42,0L20,7.59V2a1,1,0,0,0-2,0V7.59l-1.29-1.3a1,1,0,0,0-1.42,1.42l3,3a1,1,0,0,0,.33.21.94.94,0,0,0,.76,0,1,1,0,0,0,.33-.21l3-3A1,1,0,0,0,22.71,6.29ZM19,13a1,1,0,0,0-1,1v.38L16.52,12.9a2.79,2.79,0,0,0-3.93,0l-.7.7L9.41,11.12a2.85,2.85,0,0,0-3.93,0L4,12.6V7A1,1,0,0,1,5,6h8a1,1,0,0,0,0-2H5A3,3,0,0,0,2,7V19a3,3,0,0,0,3,3H17a3,3,0,0,0,3-3V14A1,1,0,0,0,19,13ZM5,20a1,1,0,0,1-1-1V15.43l2.9-2.9a.79.79,0,0,1,1.09,0l3.17,3.17,0,0L15.46,20Zm13-1a.89.89,0,0,1-.18.53L13.31,15l.7-.7a.77.77,0,0,1,1.1,0L18,17.21Z",
    width: 21,
    height: 21,
    transform: "translate(-2, -2)",
  },
};

function onlyOne(checkbox) {
  var checkboxes = document.getElementsByName("csv_plot_yaxis_check");
  checkboxes.forEach((item) => {
    if (item !== checkbox) item.checked = false;
  });
}

function add_annotation(data, yshift, popup_data, current_text = null) {
  let gd = globals.CHART_DIV;
  let x = data.x;
  let y = data.y;
  let yref = data.yref;
  let annotations = gd.layout.annotations;
  let index = -1;

  for (let i = 0; i < annotations.length; i++) {
    if (
      annotations[i].x == x &&
      annotations[i].y == y &&
      annotations[i].text == current_text
    ) {
      index = i;
      break;
    }
  }
  if (index == -1) {
    let annotation = {
      x: x,
      y: y,
      xref: "x",
      yref: yref,
      xanchor: "center",
      text: popup_data.text,
      showarrow: true,
      arrowhead: 2,
      arrowsize: 1,
      arrowwidth: 2,
      ax: x,
      ay: y + yshift,
      ayref: yref,
      axref: "x",
      bordercolor: popup_data.bordercolor,
      bgcolor: "#000000",
      borderwidth: 2,
      borderpad: 4,
      opacity: 0.8,
      font: {
        color: popup_data.color,
        size: popup_data.size,
      },
      clicktoshow: "onoff",
      captureevents: true,
    };
    annotations.push(annotation);
  } else {
    annotations[index].text = popup_data.text;
    annotations[index].font.color = popup_data.color;
    annotations[index].font.size = popup_data.size;
    annotations[index].ay = y + yshift;
    annotations[index].bordercolor = popup_data.bordercolor;
  }
  return annotations;
}

function checkFile(popup, type = false) {
  console.log("checkFile");
  let csv_file = popup.querySelector("#csv_file");
  let csv_name = popup.querySelector("#csv_name");
  let csv_type = popup.querySelector("#csv_trace_type");
  let csv_columns = popup.querySelector("#csv_columns");
  let csv_colors = popup.querySelector("#csv_colors");
  let csv_plot_yaxis_options = popup.querySelector("#csv_plot_yaxis_options");
  let csv_bar_orientation = popup.querySelector("#csv_bar_orientation");
  csv_plot_yaxis_options.style.display = "none";
  csv_bar_orientation.style.display = "none";
  csv_plot_yaxis_options.querySelector(
    "#csv_percent_change_div"
  ).style.display = "inline-block";

  if (csv_file.files.length > 0) {
    console.log("file selected");
    let file = csv_file.files[0];
    let reader = new FileReader();

    reader.onload = function (e) {
      let headers = e.target.result.split("\n")[0].split(",");
      headers = headers.map((x) => x.replace(/\r/g, ""));
      let headers_lower = headers.map((x) => x.trim().toLowerCase());
      let candle_cols = ["open", "high", "low", "close"];

      let options = "";
      for (let i = 0; i < headers.length; i++) {
        options += `<option value="${headers[i]}">${headers[i]}</option>`;
      }

      // we try to guess the type of the data from the headers
      if (type == false) {
        if (
          headers_lower
            .map(function (x) {
              return candle_cols.includes(x);
            })
            .includes(true)
        ) {
          csv_type.value = "candlestick";
        } else {
          csv_type.value = "scatter";
        }
      }
      let option_ids = ["csv_x", "csv_y"];

      csv_columns.innerHTML = "<b>Columns:</b><br>";
      if (csv_type.value == "candlestick") {
        option_ids = ["x", "open", "high", "low", "close"];
        let options_select = "";

        for (let i = 0; i < option_ids.length; i++) {
          let header_name = option_ids[i].replace(/\b[a-z]/g, (x) =>
            x.toUpperCase()
          );

          options_select += `
          <div style="display: flex; align-items: center; justify-items: space-between;">
          <label style="width: 100px;" for="csv_${option_ids[i]}">${header_name}</label>
          <select id="csv_${option_ids[i]}" style="width: 100%;">
          ${options}
          </select>
          </div>
          `;
        }
        csv_columns.innerHTML += `
        <div class="csv_column_container">${options_select}</div>
        `;

        csv_colors.innerHTML = `
                    <b>Candlestick colors:</b><br>

                    <label for="csv_increasing">Increasing</label>
                    <input type="color" id="csv_increasing" value="#00ACFF"></input>
                    <label for="csv_decreasing">Decreasing</label>
                    <input type="color" id="csv_decreasing" value="#FF0000"></input>
                `;

        for (let i = 0; i < option_ids.length; i++) {
          if (headers_lower.includes(option_ids[i])) {
            csv_columns.querySelector("#csv_" + option_ids[i]).value =
              headers[headers_lower.indexOf(option_ids[i])];
          } else if (option_ids[i] == "x" && headers_lower.includes("date")) {
            csv_columns.querySelector("#csv_x").value =
              headers[headers_lower.indexOf("date")];
          }
        }
        globals.CSV_DIV.querySelector("#csv_percent_change_div").style.display =
          "none";
      } else {
        let color_text = csv_type.value == "bar" ? "Bar color" : "Line color";
        csv_columns.innerHTML = `
                    <b>Columns:</b><br>
                    <div style="margin-top: 5px; margin-bottom: 10px;">
                      <label for="csv_x">X axis</label>
                      <select id="csv_x">
                          ${options}
                      </select>
                    </div>
                    <div style="margin-top: 5px; margin-bottom: 5px;">
                      <label for="csv_y">Y axis</label>
                      <select id="csv_y">
                          ${options}
                      </select>
                    </div>
                `;
        csv_colors.innerHTML = `
                    <label style="margin-top: 10px; margin-bottom: 10px;"
                      for="csv_color"><b>${color_text}:</b></label>
                    <input type="color" id="csv_color" value="#FFDD00"></input>
                `;

        if (headers_lower.includes("x")) {
          csv_columns.querySelector("#csv_x").value =
            headers[headers_lower.indexOf("x")];
        } else if (headers_lower.includes("date")) {
          csv_columns.querySelector("#csv_x").value =
            headers[headers_lower.indexOf("date")];
        }

        if (headers_lower.includes("y")) {
          csv_columns.querySelector("#csv_y").value =
            headers[headers_lower.indexOf("y")];
        } else if (headers_lower.includes("close")) {
          csv_columns.querySelector("#csv_y").value =
            headers[headers_lower.indexOf("close")];
        }
      }
      if (csv_type.value == "bar") {
        csv_bar_orientation.style.display = "inline-block";
        globals.CSV_DIV.querySelector("#csv_percent_change_div").style.display =
          "none";
      }

      csv_plot_yaxis_options.style.display = "inline-block";

      // we try to guess the date and time to remove from the name of the file
      // if "_" in the name of the file,
      // we assume the first 2 parts or the last 2 parts are date and time
      let filename = file.name.split(".")[0];
      csv_name.value = filename;

      try {
        if (filename.includes("_")) {
          let name_parts = filename.split("_");
          let date_regex = new RegExp("^[0-9]{8}$");

          if (name_parts.length > 2) {
            // we check if the first 2 parts are date and time
            if (date_regex.test(name_parts[0])) {
              name_parts.splice(0, 2);
            }
            // we check if the last 2 parts are date and time
            else if (date_regex.test(name_parts[name_parts.length - 2])) {
              name_parts.splice(name_parts.length - 2, 2);
            }
            csv_name.value = name_parts.join("_").replace(/openbb_/g, "");
          }
        }
      } catch (e) {
        console.log(e);
      }
    };

    reader.readAsText(file);
  }
}

function openbbFilename(data, csv = false) {
  let title = csv ? "data" : "plots";

  if (data.layout.title != undefined) {
    title = (csv ? "data_" : "") + data.layout.title.text;
  }

  globals.title = title;

  let filename = "openbb_" + title.replace(/<b>|<\/b>/g, "").replace(/ /g, "_");

  let date = new Date().toISOString().slice(0, 10).replace(/-/g, "");
  let time = new Date().toISOString().slice(11, 19).replace(/:/g, "");

  return filename + "_" + date + "_" + time;
}

function plot_text(data, popup_data, current_text = null) {
  // Plots text on the chart based on the popup_data
  // If current_text is not null, it will be replaced with the new text
  // If current_text is null, a new annotation will be added
  // popup_data is the data from the popup
  // data is the data from the chart

  console.log("plot_text");
  let gd = globals.CHART_DIV;
  let annotations = undefined;
  let yaxis = data.yref.replace("y", "yaxis");
  let yrange = gd.layout[yaxis].range;
  let yshift = (yrange[1] - yrange[0]) * 0.2;

  if (popup_data.yanchor == "below") {
    yshift = -yshift;
  }

  if (current_text == null) {
    annotations = add_annotation(data, yshift, popup_data);
  } else {
    annotations = add_annotation(data, yshift, popup_data, current_text);
  }
  let to_update = { annotations: annotations, dragmode: "pan" };
  to_update[yaxis + ".type"] = "linear";

  Plotly.update(gd, {}, to_update);
  gd.removeAllListeners("plotly_click");

  globals.TEXT_DIV = document.getElementById("popup_text");
  globals.TEXT_DIV.querySelectorAll("input").forEach(function (input) {
    if (!input.name in ["addtext_color", "addtext_border"]) {
      input.value = "";
    }
  });
  closePopup();
}

function update_color() {
  // updates the color of the last added shape
  // this function is called when the color picker is used
  let color = globals.color_picker.querySelector("#picked_color").value;
  let gd = globals.CHART_DIV;

  // if there are no shapes, we remove the color picker
  let shapes = gd.layout.shapes;
  if (!shapes || shapes.length == 0) {
    globals.color_picker.remove();
    return;
  }
  // we change last added shape color
  let last_shape = shapes[shapes.length - 1];
  last_shape.line.color = color;
  Plotly.update(gd, {}, { shapes: shapes });
}

function button_pressed(title, active = false) {
  // changes the style of the button when it is pressed
  // title is the title of the button
  // active is true if the button is active, false otherwise

  let button = globals.barButtons[title];

  if (!active) {
    button.style.border = "1px solid rgba(0, 151, 222, 1.0)";
    button.style.borderRadius = "5px";
    button.style.borderpadding = "5px";
    button.style.boxShadow = "0 0 5px rgba(0, 151, 222, 1.0)";
  } else {
    button.style.border = "transparent";
    button.style.boxShadow = "none";
  }
}

const DARK_CHARTS_TEMPLATE = {
  line: {
    up_color: "#00ACFF",
    down_color: "#e4003a",
    color: "#ffed00",
    width: 1.5,
  },
  data: {
    candlestick: [
      {
        decreasing: {
          fillcolor: "#e4003a",
          line: {
            color: "#e4003a",
          },
        },
        increasing: {
          fillcolor: "#00ACFF",
          line: {
            color: "#00ACFF",
          },
        },
        type: "candlestick",
      },
    ],
  },
  layout: {
    annotationdefaults: {
      showarrow: false,
    },
    autotypenumbers: "strict",
    colorway: [
      "#ffed00",
      "#ef7d00",
      "#e4003a",
      "#c13246",
      "#822661",
      "#48277c",
      "#005ca9",
      "#00aaff",
      "#9b30d9",
      "#af005f",
      "#5f00af",
      "#af87ff",
    ],
    dragmode: "pan",
    font: {
      family: "Fira Code",
      size: 18,
    },
    hoverlabel: {
      align: "left",
    },
    mapbox: {
      style: "dark",
    },
    hovermode: "x",
    legend: {
      bgcolor: "rgba(0, 0, 0, 0)",
      x: 0.01,
      xanchor: "left",
      y: 0.99,
      yanchor: "top",
      font: {
        size: 15,
      },
    },
    paper_bgcolor: "#000000",
    plot_bgcolor: "#000000",
    xaxis: {
      automargin: true,
      autorange: true,
      rangeslider: {
        visible: false,
      },
      showgrid: true,
      showline: true,
      tickfont: {
        size: 14,
      },
      zeroline: false,
      tick0: 1,
      title: {
        standoff: 20,
      },
      linecolor: "#F5EFF3",
      mirror: true,
      ticks: "outside",
    },
    yaxis: {
      anchor: "x",
      automargin: true,
      fixedrange: false,
      zeroline: false,
      showgrid: true,
      showline: true,
      side: "right",
      tick0: 0.5,
      title: {
        standoff: 20,
      },
      gridcolor: "#283442",
      linecolor: "#F5EFF3",
      mirror: true,
      ticks: "outside",
    },
  },
};

const LIGHT_CHARTS_TEMPLATE = {
  line: {
    up_color: "#009600",
    down_color: "#c80000",
    color: "#0d0887",
    width: 1.5,
  },
  data: {
    barpolar: [
      {
        marker: {
          line: {
            color: "white",
            width: 0.5,
          },
          pattern: {
            fillmode: "overlay",
            size: 10,
            solidity: 0.2,
          },
        },
        type: "barpolar",
      },
    ],
    bar: [
      {
        error_x: {
          color: "#2a3f5f",
        },
        error_y: {
          color: "#2a3f5f",
        },
        marker: {
          line: {
            color: "white",
            width: 0.5,
          },
          pattern: {
            fillmode: "overlay",
            size: 10,
            solidity: 0.2,
          },
        },
        type: "bar",
      },
    ],
    carpet: [
      {
        aaxis: {
          endlinecolor: "#2a3f5f",
          gridcolor: "#C8D4E3",
          linecolor: "#C8D4E3",
          minorgridcolor: "#C8D4E3",
          startlinecolor: "#2a3f5f",
        },
        baxis: {
          endlinecolor: "#2a3f5f",
          gridcolor: "#C8D4E3",
          linecolor: "#C8D4E3",
          minorgridcolor: "#C8D4E3",
          startlinecolor: "#2a3f5f",
        },
        type: "carpet",
      },
    ],
    choropleth: [
      {
        colorbar: {
          outlinewidth: 0,
          ticks: "",
        },
        type: "choropleth",
      },
    ],
    contourcarpet: [
      {
        colorbar: {
          outlinewidth: 0,
          ticks: "",
        },
        type: "contourcarpet",
      },
    ],
    contour: [
      {
        colorbar: {
          outlinewidth: 0,
          ticks: "",
        },
        colorscale: [
          [0.0, "#0d0887"],
          [0.1111111111111111, "#46039f"],
          [0.2222222222222222, "#7201a8"],
          [0.3333333333333333, "#9c179e"],
          [0.4444444444444444, "#bd3786"],
          [0.5555555555555556, "#d8576b"],
          [0.6666666666666666, "#ed7953"],
          [0.7777777777777778, "#fb9f3a"],
          [0.8888888888888888, "#fdca26"],
          [1.0, "#f0f921"],
        ],
        type: "contour",
      },
    ],
    heatmapgl: [
      {
        colorbar: {
          outlinewidth: 0,
          ticks: "",
        },
        colorscale: [
          [0.0, "#0d0887"],
          [0.1111111111111111, "#46039f"],
          [0.2222222222222222, "#7201a8"],
          [0.3333333333333333, "#9c179e"],
          [0.4444444444444444, "#bd3786"],
          [0.5555555555555556, "#d8576b"],
          [0.6666666666666666, "#ed7953"],
          [0.7777777777777778, "#fb9f3a"],
          [0.8888888888888888, "#fdca26"],
          [1.0, "#f0f921"],
        ],
        type: "heatmapgl",
      },
    ],
    heatmap: [
      {
        colorbar: {
          outlinewidth: 0,
          ticks: "",
        },
        colorscale: [
          [0.0, "#0d0887"],
          [0.1111111111111111, "#46039f"],
          [0.2222222222222222, "#7201a8"],
          [0.3333333333333333, "#9c179e"],
          [0.4444444444444444, "#bd3786"],
          [0.5555555555555556, "#d8576b"],
          [0.6666666666666666, "#ed7953"],
          [0.7777777777777778, "#fb9f3a"],
          [0.8888888888888888, "#fdca26"],
          [1.0, "#f0f921"],
        ],
        type: "heatmap",
      },
    ],
    histogram2dcontour: [
      {
        colorbar: {
          outlinewidth: 0,
          ticks: "",
        },
        colorscale: [
          [0.0, "#0d0887"],
          [0.1111111111111111, "#46039f"],
          [0.2222222222222222, "#7201a8"],
          [0.3333333333333333, "#9c179e"],
          [0.4444444444444444, "#bd3786"],
          [0.5555555555555556, "#d8576b"],
          [0.6666666666666666, "#ed7953"],
          [0.7777777777777778, "#fb9f3a"],
          [0.8888888888888888, "#fdca26"],
          [1.0, "#f0f921"],
        ],
        type: "histogram2dcontour",
      },
    ],
    histogram2d: [
      {
        colorbar: {
          outlinewidth: 0,
          ticks: "",
        },
        colorscale: [
          [0.0, "#0d0887"],
          [0.1111111111111111, "#46039f"],
          [0.2222222222222222, "#7201a8"],
          [0.3333333333333333, "#9c179e"],
          [0.4444444444444444, "#bd3786"],
          [0.5555555555555556, "#d8576b"],
          [0.6666666666666666, "#ed7953"],
          [0.7777777777777778, "#fb9f3a"],
          [0.8888888888888888, "#fdca26"],
          [1.0, "#f0f921"],
        ],
        type: "histogram2d",
      },
    ],
    histogram: [
      {
        marker: {
          pattern: {
            fillmode: "overlay",
            size: 10,
            solidity: 0.2,
          },
        },
        type: "histogram",
      },
    ],
    mesh3d: [
      {
        colorbar: {
          outlinewidth: 0,
          ticks: "",
        },
        type: "mesh3d",
      },
    ],
    parcoords: [
      {
        line: {
          colorbar: {
            outlinewidth: 0,
            ticks: "",
          },
        },
        type: "parcoords",
      },
    ],
    pie: [
      {
        automargin: true,
        type: "pie",
      },
    ],
    scatter3d: [
      {
        line: {
          colorbar: {
            outlinewidth: 0,
            ticks: "",
          },
        },
        marker: {
          colorbar: {
            outlinewidth: 0,
            ticks: "",
          },
        },
        type: "scatter3d",
      },
    ],
    scattercarpet: [
      {
        marker: {
          colorbar: {
            outlinewidth: 0,
            ticks: "",
          },
        },
        type: "scattercarpet",
      },
    ],
    scattergeo: [
      {
        marker: {
          colorbar: {
            outlinewidth: 0,
            ticks: "",
          },
        },
        type: "scattergeo",
      },
    ],
    scattergl: [
      {
        marker: {
          colorbar: {
            outlinewidth: 0,
            ticks: "",
          },
        },
        type: "scattergl",
      },
    ],
    scattermapbox: [
      {
        marker: {
          colorbar: {
            outlinewidth: 0,
            ticks: "",
          },
        },
        type: "scattermapbox",
      },
    ],
    scatterpolargl: [
      {
        marker: {
          colorbar: {
            outlinewidth: 0,
            ticks: "",
          },
        },
        type: "scatterpolargl",
      },
    ],
    scatterpolar: [
      {
        marker: {
          colorbar: {
            outlinewidth: 0,
            ticks: "",
          },
        },
        type: "scatterpolar",
      },
    ],
    scatter: [
      {
        fillpattern: {
          fillmode: "overlay",
          size: 10,
          solidity: 0.2,
        },
        type: "scatter",
      },
    ],
    scatterternary: [
      {
        marker: {
          colorbar: {
            outlinewidth: 0,
            ticks: "",
          },
        },
        type: "scatterternary",
      },
    ],
    surface: [
      {
        colorbar: {
          outlinewidth: 0,
          ticks: "",
        },
        colorscale: [
          [0.0, "#0d0887"],
          [0.1111111111111111, "#46039f"],
          [0.2222222222222222, "#7201a8"],
          [0.3333333333333333, "#9c179e"],
          [0.4444444444444444, "#bd3786"],
          [0.5555555555555556, "#d8576b"],
          [0.6666666666666666, "#ed7953"],
          [0.7777777777777778, "#fb9f3a"],
          [0.8888888888888888, "#fdca26"],
          [1.0, "#f0f921"],
        ],
        type: "surface",
      },
    ],
    table: [
      {
        cells: {
          fill: {
            color: "#EBF0F8",
          },
          line: {
            color: "white",
          },
        },
        header: {
          fill: {
            color: "#C8D4E3",
          },
          line: {
            color: "white",
          },
        },
        type: "table",
      },
    ],
    candlestick: [
      {
        decreasing: {
          fillcolor: "#c80000",
          line: {
            color: "#990000",
          },
        },
        increasing: {
          fillcolor: "#009600",
          line: {
            color: "#007500",
          },
        },
        type: "candlestick",
      },
    ],
  },
  layout: {
    annotationdefaults: {
      arrowcolor: "#2a3f5f",
      arrowhead: 0,
      arrowwidth: 1,
      showarrow: false,
    },
    autotypenumbers: "strict",
    coloraxis: {
      colorbar: {
        outlinewidth: 0,
        ticks: "",
      },
    },
    colorscale: {
      diverging: [
        [0, "#8e0152"],
        [0.1, "#c51b7d"],
        [0.2, "#de77ae"],
        [0.3, "#f1b6da"],
        [0.4, "#fde0ef"],
        [0.5, "#f7f7f7"],
        [0.6, "#e6f5d0"],
        [0.7, "#b8e186"],
        [0.8, "#7fbc41"],
        [0.9, "#4d9221"],
        [1, "#276419"],
      ],
      sequential: [
        [0.0, "#0d0887"],
        [0.1111111111111111, "#46039f"],
        [0.2222222222222222, "#7201a8"],
        [0.3333333333333333, "#9c179e"],
        [0.4444444444444444, "#bd3786"],
        [0.5555555555555556, "#d8576b"],
        [0.6666666666666666, "#ed7953"],
        [0.7777777777777778, "#fb9f3a"],
        [0.8888888888888888, "#fdca26"],
        [1.0, "#f0f921"],
      ],
      sequentialminus: [
        [0.0, "#0d0887"],
        [0.1111111111111111, "#46039f"],
        [0.2222222222222222, "#7201a8"],
        [0.3333333333333333, "#9c179e"],
        [0.4444444444444444, "#bd3786"],
        [0.5555555555555556, "#d8576b"],
        [0.6666666666666666, "#ed7953"],
        [0.7777777777777778, "#fb9f3a"],
        [0.8888888888888888, "#fdca26"],
        [1.0, "#f0f921"],
      ],
    },
    colorway: [
      "#254495",
      "#c13246",
      "#48277c",
      "#e4003a",
      "#ef7d00",
      "#822661",
      "#ffed00",
      "#00aaff",
      "#9b30d9",
      "#af005f",
      "#5f00af",
      "#af87ff",
    ],
    font: {
      color: "#2a3f5f",
    },
    geo: {
      bgcolor: "white",
      lakecolor: "white",
      landcolor: "white",
      showlakes: true,
      showland: true,
      subunitcolor: "#C8D4E3",
    },
    hoverlabel: {
      align: "left",
    },
    hovermode: "x",
    mapbox: {
      style: "light",
    },
    paper_bgcolor: "white",
    plot_bgcolor: "white",
    polar: {
      angularaxis: {
        gridcolor: "#EBF0F8",
        linecolor: "#EBF0F8",
        ticks: "",
      },
      bgcolor: "white",
      radialaxis: {
        gridcolor: "#EBF0F8",
        linecolor: "#EBF0F8",
        ticks: "",
      },
    },
    scene: {
      xaxis: {
        backgroundcolor: "white",
        gridcolor: "#DFE8F3",
        gridwidth: 2,
        linecolor: "#EBF0F8",
        showbackground: true,
        ticks: "",
        zerolinecolor: "#EBF0F8",
      },
      yaxis: {
        backgroundcolor: "white",
        gridcolor: "#DFE8F3",
        gridwidth: 2,
        linecolor: "#EBF0F8",
        showbackground: true,
        ticks: "",
        zerolinecolor: "#EBF0F8",
      },
      zaxis: {
        backgroundcolor: "white",
        gridcolor: "#DFE8F3",
        gridwidth: 2,
        linecolor: "#EBF0F8",
        showbackground: true,
        ticks: "",
        zerolinecolor: "#EBF0F8",
      },
    },
    shapedefaults: {
      line: {
        color: "#2a3f5f",
      },
    },
    ternary: {
      aaxis: {
        gridcolor: "#DFE8F3",
        linecolor: "#A2B1C6",
        ticks: "",
      },
      baxis: {
        gridcolor: "#DFE8F3",
        linecolor: "#A2B1C6",
        ticks: "",
      },
      bgcolor: "white",
      caxis: {
        gridcolor: "#DFE8F3",
        linecolor: "#A2B1C6",
        ticks: "",
      },
    },
    title: {
      x: 0.05,
    },
    xaxis: {
      automargin: true,
      ticks: "",
      zerolinewidth: 2,
      rangeslider: {
        visible: false,
      },
      showgrid: true,
      showline: true,
      tickfont: {
        size: 15,
      },
      mirror: true,
      zeroline: false,
    },
    yaxis: {
      automargin: true,
      ticks: "",
      tickfont: {
        size: 15,
      },
      zerolinewidth: 2,
      fixedrange: false,
      nticks: 8,
      showgrid: true,
      showline: true,
      side: "right",
      mirror: true,
      zeroline: false,
    },
    dragmode: "pan",
    legend: {
      bgcolor: "rgba(0, 0, 0, 0)",
      x: 1.03,
      xanchor: "left",
      y: 0.99,
      yanchor: "top",
    },
  },
};
