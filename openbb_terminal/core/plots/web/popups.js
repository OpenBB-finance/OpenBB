function get_popup(data = null, popup_id = null) {
  let popup = null;
  popup_id = popup_id.replace("popup_", "");
  const style =
    "padding: 5px 2px 2px 5px !important; margin: 2px 0 !important;";

  if (popup_id == "title") {
    let title = globals.title;
    data = globals.CHART_DIV.layout;
    let yaxes = Object.keys(data).filter((k) => k.startsWith("yaxis"));
    let xaxes = Object.keys(data).filter((k) => k.startsWith("xaxis"));

    globals.TITLE_DIV.innerHTML = `
        <div style="display:flex; flex-direction: column; gap: 6px;">
            <div>
            <label for="title_text">Title:</label>
            <textarea
              id="title_text" style="${style} width: 100%; max-width: 100%;
              max-height: 200px; margin-top: 8px;" rows="2" cols="20"
              value="${title}">${title}</textarea>
            </div>
            <div id="xaxis_div"></div>
            <div id="yaxis_div"></div>
        </div>

        <div style="float: right; margin-top: 20px;">
        <button class="_btn-tertiary" id="title_cancel" onclick="closePopup()">Cancel</button>
        <button class="_btn" id="title_submit" onclick="on_submit('title')">Submit</button>
        </div>
        `;

    // if there are multiple titles we create an input for each
    let yaxis_div = "";
    for (let i = 0; i < yaxes.length; i++) {
      if (data[yaxes[i]]?.title?.text != undefined) {
        let title = data[yaxes[i]].title.text;
        yaxis_div += `
            <div style="margin-top: 10px;">
            <label for="title_${yaxes[i]}">Y axis ${i + 1}:</label>
            <input id="title_${
              yaxes[i]
            }" style="${style}" type="text" value="${title}"></input>
            </div>
            `;
      }
    }
    if (yaxis_div != "") {
      globals.TITLE_DIV.querySelector("#yaxis_div").innerHTML = yaxis_div;
    }

    let xaxis_div = "";
    for (let i = 0; i < xaxes.length; i++) {
      if (data[xaxes[i]]?.title?.text != undefined) {
        let title = data[xaxes[i]].title.text;
        xaxis_div += `
            <div style="margin-top: 10px;">
            <label for="title_${xaxes[i]}">X axis ${i + 1}:</label>
            <input id="title_${
              xaxes[i]
            }" style="${style}" type="text" value="${title}"></input>
            </div>
            `;
      }
    }
    if (xaxis_div != "") {
      globals.TITLE_DIV.querySelector("#xaxis_div").innerHTML = xaxis_div;
    }

    // when opening the popup, we make sure to focus on the title input
    globals.TITLE_DIV.style.display = "inline-block";
    globals.TITLE_DIV.querySelector("#title_text").focus();
    popup = globals.TITLE_DIV;
  } else if (popup_id == "text") {
    let has_annotation = data == undefined ? false : true;
    if (data == undefined) {
      data = {
        text: "",
        font: {
          color: "#0088CC",
          size: 18,
        },
        bordercolor: "#822661",
      };
    }

    // we replace <br> with \n so that the textarea can display the text properly
    data.text = data.text.replace(/<br>/g, "\n");

    let yanchor =
      globals.TEXT_DIV.querySelector("#addtext_above") == null
        ? "above"
        : globals.TEXT_DIV.querySelector("#addtext_above").checked
        ? "above"
        : "below";

    globals.TEXT_DIV.innerHTML = `
    <div style="margin-bottom: 20px;">
        <label for="popup_textarea"><b>Text:</b>
        <div id="popup_textarea_warning" class="popup_warning">Text is required</div></label><br>
        <textarea id="addtext_textarea" style="${style}
          width: 100%; max-width: 100%; max-height: 200px;
          margin-top: 8px;" rows="4" cols="50" value="${data.text}"
            placeholder="Enter text here">${data.text}</textarea><br>
        </div>
        <div style="display:flex;justify-content: space-between;">
            <div>
            <label for="addtext_color"><b>Font color:</b></label>
            <input type="color" id="addtext_color" value="${
              data.font.color
            }"></input>
            </div>
            <div>
            <label for="addtext_border"><b>Border color:</b></label>
            <input type="color" id="addtext_border" value="${
              data.bordercolor
            }"></input>
            </div>
        </div><br>

        <div style="display:flex;justify-content: space-between;">
        <div>
            <label for="addtext_size"><b>Font size:</b></label>
            <input style="${style} width: 45px;" type="number" id="addtext_size" value="${
      data.font.size
    }"></input>
        </div>
        <div>
            <label for="addtext_above"><b>Position (Above):</b></label>
            <input type="checkbox" id="addtext_above" name="check"
                value="above" ${yanchor == "above" ? "checked" : ""}></input>
                </div>
        </div><br>
        `;

    if (has_annotation) {
      globals.TEXT_DIV.innerHTML += `
      <div style="float: right; margin-top: 20px;">
            <button class="_btn-tertiary" id="addtext_cancel" onclick="closePopup()">Cancel</button>
            <button class="_btn" id="addtext_delete" onclick="on_delete('text')">Delete</button>
            <button class="_btn" id="addtext_submit" onclick="on_submit('text', true)">Submit</button>
            <input id="addtext_annotation" type="hidden" value='${JSON.stringify(
              data
            )}'></input>
            </div>
            `;
    } else {
      globals.TEXT_DIV.innerHTML += `
      <div style="float: right; margin-top: 20px;">
            <button class="_btn-tertiary" id="addtext_cancel" onclick="closePopup()">Cancel</button>
            <button class="_btn" id="addtext_submit" onclick="on_submit('text')">Submit</button>
    </div>
            `;

      if (globals.TEXT_DIV.querySelector("#addtext_annotation") != null) {
        globals.TEXT_DIV.querySelector("#addtext_annotation").remove();
      }
    }

    // when opening the popup, we make sure to focus on the textarea
    globals.TEXT_DIV.style.display = "inline-block";
    globals.TEXT_DIV.querySelector("#addtext_textarea").focus();
    popup = globals.TEXT_DIV;
  } else if (popup_id == "csv") {
    globals.CSV_DIV.style.display = "inline-block";
    popup = globals.CSV_DIV;
    console.log("csv");
  } else if (popup_id == "upload") {
    globals.TEXT_DIV.style.display = "inline-block";
    globals.TEXT_DIV.innerHTML = `
    <div>
      <p>Media preview (you can share it on twitter):</p>
      <a style="margin-top: 10px;" href="${data.url}" target="_blank" rel="noreferrer noopener">${data.url}</a>
      <div style="margin-top: 10px; float: right;">
      <button onclick="closePopup()" style="margin-top: 10px;" class="_btn-tertiary">Close</button>
      <a
      class="_btn"
      href="https://twitter.com/intent/tweet?text=Check this chart from @openbb_finance - ${data.url}"
      >Share</a>
      <button onclick="navigator.clipboard.writeText('${data.url}')" style="margin-top: 10px;"
        class="_btn">Copy to clipboard</button>
      </div>
      </div>
      `;
    popup = globals.TEXT_DIV;
    console.log("upload");
  }

  let popup_divs = [globals.TITLE_DIV, globals.TEXT_DIV, globals.CSV_DIV];
  popup_divs.forEach(function (div) {
    if (div.id != popup.id) {
      div.style.display = "none";
    }
  });

  return popup;
}

function get_popup_data(popup_id = null) {
  // popup_id is either 'title', 'text', or 'csv' (for now)
  // and is used to determine which popup to get data from
  let data = null;

  if (popup_id == "title") {
    data = { title: globals.TITLE_DIV.querySelector("#title_text").value };

    let xaxis_div = globals.TITLE_DIV.querySelector("#xaxis_div");
    let yaxis_div = globals.TITLE_DIV.querySelector("#yaxis_div");
    console.log("xaxis_div: ", xaxis_div, "yaxis_div: ", yaxis_div);

    if (xaxis_div != null) {
      // We query all inputs that start with 'title_xaxis'
      let xaxis_inputs = xaxis_div.querySelectorAll(
        "input[id^=title_xaxis], select[id^=title_xaxis]"
      );
      xaxis_inputs.forEach(function (input) {
        let xaxis_id = input.id.replace("title_", "");
        data[xaxis_id] = input.value;
      });
    }

    if (yaxis_div != null) {
      // We query all inputs that start with 'title_yaxis'
      let yaxis_inputs = yaxis_div.querySelectorAll(
        "input[id^=title_yaxis], select[id^=title_yaxis]"
      );
      yaxis_inputs.forEach(function (input) {
        let yaxis_id = input.id.replace("title_", "");
        data[yaxis_id] = input.value;
      });
    }
    console.log("Title data:", data);
  } else if (popup_id == "text") {
    data = {
      text: globals.TEXT_DIV.querySelector("#addtext_textarea").value,
      color: globals.TEXT_DIV.querySelector("#addtext_color").value,
      size: globals.TEXT_DIV.querySelector("#addtext_size").value,
      yanchor: globals.TEXT_DIV.querySelector("#addtext_above").checked
        ? "above"
        : "below",
      bordercolor: globals.TEXT_DIV.querySelector("#addtext_border").value,
    };
    if (globals.TEXT_DIV.querySelector("#addtext_annotation") != null) {
      data.annotation = JSON.parse(
        globals.TEXT_DIV.querySelector("#addtext_annotation").value
      );
    }

    // we replace \n with <br> so that line breaks are displayed properly on the graph
    data.text = data.text.replace(/\n/g, "<br>");
    console.log("Text data:", data);
  } else if (popup_id == "csv") {
    let trace_type = globals.CSV_DIV.querySelector("#csv_trace_type").value;
    if (trace_type == "candlestick") {
      data = {
        x: globals.CSV_DIV.querySelector("#csv_x").value,
        open: globals.CSV_DIV.querySelector("#csv_open").value,
        high: globals.CSV_DIV.querySelector("#csv_high").value,
        low: globals.CSV_DIV.querySelector("#csv_low").value,
        close: globals.CSV_DIV.querySelector("#csv_close").value,
        increasing: globals.CSV_DIV.querySelector("#csv_increasing").value,
        decreasing: globals.CSV_DIV.querySelector("#csv_decreasing").value,
        same_yaxis: globals.CSV_DIV.querySelector("#csv_same_yaxis").checked
          ? true
          : false,
      };
    } else if (trace_type == "scatter") {
      data = {
        x: globals.CSV_DIV.querySelector("#csv_x").value,
        y: globals.CSV_DIV.querySelector("#csv_y").value,
        color: globals.CSV_DIV.querySelector("#csv_color").value,
        percent_change: globals.CSV_DIV.querySelector("#csv_percent_change")
          .checked
          ? true
          : false,
        same_yaxis: globals.CSV_DIV.querySelector("#csv_same_yaxis").checked
          ? true
          : false,
      };
    } else if (trace_type == "bar") {
      let orientation = globals.CSV_DIV.querySelector("#csv_bar_horizontal")
        .checked
        ? "h"
        : "v";
      data = {
        x: globals.CSV_DIV.querySelector("#csv_x").value,
        y: globals.CSV_DIV.querySelector("#csv_y").value,
        color: globals.CSV_DIV.querySelector("#csv_color").value,
        same_yaxis: globals.CSV_DIV.querySelector("#csv_same_yaxis").checked
          ? true
          : false,
        orientation: orientation,
      };
    }
    data.trace_type = trace_type;
    data.name = globals.CSV_DIV.querySelector("#csv_name").value;
    console.log("CSV data:", data);
    data.file = globals.CSV_DIV.querySelector("#csv_file");
  }
  return data;
}

const trace_defaults = {
  overlaying: "y",
  side: "left",
  tickfont: { size: 12 },
  tickpadding: 5,
  showgrid: false,
  showline: false,
  showticklabels: true,
  showlegend: true,
  zeroline: false,
  anchor: "x",
  type: "linear",
  autorange: true,
};

function on_submit(popup_id, on_annotation = null) {
  // popup_id is either 'title', 'text', or 'csv' (for now)
  // and is used to determine which popup to get data from
  let popup_data = get_popup_data(popup_id);
  let gd = globals.CHART_DIV;
  Plotly.update(gd, {}, { hovermode: "closest" });

  if (popup_id == "text") {
    if (!popup_data.text == "") {
      if ("annotation" in popup_data) {
        let current_text = popup_data.annotation.text;
        let data = {
          x: popup_data.annotation.x,
          y: popup_data.annotation.y,
          yref: popup_data.annotation.yref,
        };
        plot_text(data, popup_data, current_text);
        return;
      }

      gd.on("plotly_clickannotation", function (eventData) {
        console.log("plotly_clickannotation", eventData);
        let annotation = eventData.annotation;
        openPopup("popup_text");
        get_popup(annotation, (popup_id = "text"));

        if (on_annotation != null) {
          let data = {
            x: popup_data.annotation.x,
            y: popup_data.annotation.y,
            yref: popup_data.annotation.yref,
          };
          plot_text(data, popup_data, popup_data.annotation.text);
        }
        Plotly.update(gd, {}, { hovermode: "x" });
      });

      let clickHandler = function (eventData) {
        console.log("plotly_click", eventData);
        let x = eventData.points[0].x;
        let yaxis = eventData.points[0].fullData.yaxis;
        let y = 0;

        // We need to check if the trace is a candlestick or not
        // this is because the y value is stored in the high or low
        if (eventData.points[0].y != undefined) {
          y = eventData.points[0].y;
        } else if (eventData.points[0].low != undefined) {
          if (popup_data.yanchor == "below") {
            y = eventData.points[0].low;
          } else {
            y = eventData.points[0].high;
          }
        }
        let data = {
          x: x,
          y: y,
          yref: yaxis,
        };
        plot_text(data, popup_data);
        Plotly.update(gd, {}, { hovermode: "x" });
      };

      Plotly.update(gd, {}, { dragmode: "select" });
      gd.on("plotly_click", clickHandler);
    } else {
      let textarea = globals.TEXT_DIV.querySelector("#addtext_textarea");
      document.getElementById("popup_textarea_warning").style.display = "block";
      textarea.style.border = "1px solid red";
      textarea.focus();

      globals.TEXT_DIV.style.display = "inline-block";
      return;
    }
  } else if (popup_id == "title") {
    document.getElementById("title").innerHTML = popup_data.title;

    let to_update = {};

    Object.keys(popup_data).forEach(function (key) {
      if (key != "title") {
        to_update[key + ".title"] = popup_data[key];
      }
      if (key.includes("yaxis")) {
        to_update[key + ".type"] = "linear";
      }
    });

    console.log(to_update);

    Plotly.update(gd, {}, to_update);
  } else if (popup_id == "csv") {
    console.log("got popup file");
    let popup_file = popup_data.file;

    if (popup_file.files.length > 0) {
      console.log("file selected");

      let file = popup_file.files[0];
      let popup_file_reader = new FileReader();
      popup_file_reader.onload = function (e) {
        let lines = e.target.result
          .split("\n")
          .map((x) => x.replace(/\r/g, ""));
        let data = [];
        let headers = lines[0].split(",");
        let trace = {};

        for (let i = 1; i < lines.length; i++) {
          let obj = {};
          let currentline = lines[i].split(",");
          for (let j = 0; j < headers.length; j++) {
            obj[headers[j]] = currentline[j];
          }
          data.push(obj);
        }

        // We get main plotly trace to get the x/y axis
        let main_trace = gd.data[0];
        gd.data.forEach((trace) => {
          if (globals.added_traces.indexOf(trace.name) == -1) {
            trace.showlegend = false;
          }
        });

        // We check how many yaxis have ticklabels on the left
        let left_yaxis_ticks = Object.keys(gd.layout)
          .filter((k) => k.startsWith("yaxis"))
          .map((k) => gd.layout[k])
          .filter(
            (yaxis) =>
              yaxis.side == "left" &&
              (yaxis.overlaying == "y" ||
                (yaxis.fixedrange != undefined && yaxis.fixedrange == true))
          ).length;

        // Multiply by 5 to get the xshift for cmd source text
        let add_xshift = Math.min(left_yaxis_ticks * 5, 30);

        // We set showlegend's to true
        main_trace.showlegend = true;
        gd.layout.showlegend = true;

        // Just in case xaxis/yaxis is not defined
        if (main_trace.xaxis == undefined) {
          main_trace.xaxis = "x";
        }
        if (main_trace.yaxis == undefined) {
          main_trace.yaxis = "y";
        }

        // Set the yaxis id
        let yaxis_id = main_trace.yaxis;
        let yaxis;

        // If we want to plot on a secondary yaxis
        // we get the number of yaxis and add 1 to it
        if (popup_data.same_yaxis == false) {
          let yaxes = Object.keys(gd.layout)
            .filter((k) => k.startsWith("yaxis"))
            .map((k) => gd.layout[k]);

          yaxis = `y${yaxes.length + 1}`;
          yaxis_id = `yaxis${yaxes.length + 1}`;
          console.log(`yaxis: ${yaxis} ${yaxis_id}`);

          // If percent change is true we set the yaxis id
          // in the globals so we can use it later
          if (
            globals.csv_yaxis_id == null &&
            popup_data.percent_change == true
          ) {
            globals.csv_yaxis_id = yaxis_id;
            globals.csv_yaxis = yaxis;
          }
        } else {
          // Plot on the same yaxis
          yaxis = main_trace.yaxis.replace("yaxis", "y");
        }

        // We get the yaxis ticksuffix
        let ticksuffix = left_yaxis_ticks > 0 ? "     " : "";
        if (globals.percent_yaxis_added || globals.added_traces.length > 0) {
          ticksuffix = "       ".repeat(left_yaxis_ticks);
        }

        // Bar trace
        if (popup_data.trace_type == "bar") {
          trace = {
            x: data.map(function (row) {
              return row[popup_data.x];
            }),
            y: data.map(function (row) {
              return row[popup_data.y];
            }),
            type: popup_data.trace_type,
            name: popup_data.name,
            marker: { color: popup_data.color, opacity: 0.7 },
            orientation: popup_data.orientation,
            showlegend: true,
            yaxis: yaxis,
          };
        }

        // Candlestick trace
        if (popup_data.trace_type == "candlestick") {
          trace = {
            x: data.map(function (row) {
              return row[popup_data.x];
            }),
            open: data.map(function (row) {
              return row[popup_data.open];
            }),
            high: data.map(function (row) {
              return row[popup_data.high];
            }),
            low: data.map(function (row) {
              return row[popup_data.low];
            }),
            close: data.map(function (row) {
              return row[popup_data.close];
            }),
            type: popup_data.trace_type,
            name: popup_data.name,
            increasing: { line: { color: popup_data.increasing } },
            decreasing: { line: { color: popup_data.decreasing } },
            showlegend: true,
            yaxis: yaxis,
          };
        }

        // Scatter trace
        if (popup_data.trace_type == "scatter") {
          // We get the first non null value
          orginal_data = data;
          let non_null = data.findIndex(
            (x) => x[popup_data.y] != null && x[popup_data.y] != 0
          );
          console.log(`non_null: ${non_null} ${data[non_null][popup_data.y]}`);

          trace = {
            x: data.map(function (row) {
              return row[popup_data.x];
            }),
            y: data.map(function (row) {
              if (popup_data.percent_change) {
                return (
                  (row[popup_data.y] - data[non_null][popup_data.y]) /
                  data[non_null][popup_data.y]
                );
              } else {
                return row[popup_data.y];
              }
            }),
            type: popup_data.trace_type,
            mode: "lines",
            name: popup_data.name,
            line: { color: popup_data.color },
            customdata: data.map(function (row) {
              return row[popup_data.y];
            }),
            hovertemplate: "%{customdata}<extra></extra>",
            showlegend: true,
            connectgaps: true,
            xaxis: main_trace.xaxis,
            yaxis: popup_data.percent_change ? globals.csv_yaxis : yaxis,
          };

          // For the percent change we add a new yaxis
          // if it doesn't exist
          if (
            !globals.percent_yaxis_added &&
            popup_data.percent_change == true &&
            popup_data.same_yaxis == false
          ) {
            gd.layout[yaxis_id] = {
              ...trace_defaults,
              title: {
                text: "% Change",
                font: {
                  size: 14,
                },
                standoff: 0,
              },
              ticksuffix: ticksuffix,
              tickformat: ".0%",
            };
            globals.percent_yaxis_added = true;
            if (globals.cmd_src_idx != null) {
              let xshift = gd.layout.annotations[globals.cmd_src_idx].xshift;
              xshift -= left_yaxis_ticks > 0 ? 50 + add_xshift : 35;

              // just in case we have a lot of yaxis
              xshift += xshift < -320 ? 10 + 2 * left_yaxis_ticks : 0;

              gd.layout.annotations[globals.cmd_src_idx].xshift = xshift;
              gd.layout.margin.l += left_yaxis_ticks > 0 ? 50 + add_xshift : 45;
            }
          }
        }

        // New yaxis and not percent change
        if (!popup_data.percent_change && popup_data.same_yaxis == false) {
          gd.layout[yaxis_id] = {
            ...trace_defaults,
            title: {
              text: popup_data.name,
              font: {
                size: 14,
              },
              standoff: 0,
            },
            ticksuffix: ticksuffix,
            layer: "below traces",
          };
          if (globals.cmd_src_idx != null) {
            let xshift = gd.layout.annotations[globals.cmd_src_idx].xshift;
            xshift -= left_yaxis_ticks > 0 ? 40 + add_xshift : 40;

            // just in case we have a lot of yaxis
            xshift += xshift < -320 ? 10 + 2 * left_yaxis_ticks : 0;

            gd.layout.annotations[globals.cmd_src_idx].xshift = xshift;
            gd.layout.margin.l += left_yaxis_ticks > 0 ? 50 : 45;
          }
        }
        console.log("trace: ", trace);

        globals.added_traces.push(trace.name);

        Plotly.addTraces(gd, trace);

        if (globals.csv_yaxis_id != null) {
          gd.layout[globals.csv_yaxis_id].type = "linear";
        }
        Plotly.react(gd, gd.data, gd.layout);

        // We empty the fields and innerHTML after the plot is made
        globals.CSV_DIV.querySelector("#csv_colors").innerHTML = "";
        globals.CSV_DIV.querySelector("#csv_columns").innerHTML = "";
        globals.CSV_DIV.querySelector("#csv_plot_yaxis_options").style.display =
          "none";

        globals.CSV_DIV.querySelectorAll("input").forEach(function (input) {
          input.value = "";
        });
        globals.CSV_DIV.querySelectorAll("textarea").forEach(function (input) {
          input.value = "";
        });
      };

      popup_file_reader.readAsText(file);
    }
  }
  closePopup();
}

function on_cancel() {
  // We close any popup that is open
  closePopup();
}

function on_delete(popup_id) {
  let gd = globals.CHART_DIV;
  closePopup();

  if (popup_id == "text") {
    let annotation = JSON.parse(
      globals.TEXT_DIV.querySelector("#addtext_annotation").value
    );
    gd.layout.annotations.splice(gd.layout.annotations.indexOf(annotation), 1);
    gd.layout.dragmode = "pan";

    Plotly.react(gd, gd.data, gd.layout);

    globals.TEXT_DIV.style.display = "none";
  }
}

function closePopup() {
  // We set the display to none to hide the popup overlay
  var popup = document.getElementById("popup_overlay");
  popup.style.display = "none";
}

function openPopup(popup_id, popup_data = null) {
  // We make sure to close the incase there is a popup already open
  closePopup();
  var overlay = document.getElementById("popup_overlay");
  // We get the popup div and set the display to block to show the popup
  overlay.style.display = "block";
  get_popup(popup_data, popup_id);
}
