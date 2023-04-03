const ICONS = {
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
    path: "M512 0C229.376 0 0 229.376 0 512s229.376 512 512 512 512-229.376 512-512S794.624 0 512 0zM512 896C264.192 896 64 695.808 64 448S264.192 64 512 64s448 200.192 448 448-200.192 448-448 448z m0-768c-141.312 0-256 114.688-256 256s114.688 256 256 256 256-114.688 256-256-114.688-256-256-256z m0 448c-70.656 0-128-57.344-128-128s57.344-128 128-128 128 57.344 128 128-57.344 128-128 128z m0-192c-35.328 0-64 28.672-64 64s28.672 64 64 64 64-28.672 64-64-28.672-64-64-64z",
    width: 1024,
    height: 1024,
  },
  uploadImage: {
    path: "M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5",
    width: 1024,
    height: 1024,
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
    button.style.border = "1px solid rgba(255, 0, 0, 0.7)";
    button.style.borderRadius = "5px";
    button.style.boxShadow = "0 0 5px rgba(255, 0, 0, 0.7)";
  } else {
    button.style.border = "transparent";
    button.style.boxShadow = "none";
  }
}
