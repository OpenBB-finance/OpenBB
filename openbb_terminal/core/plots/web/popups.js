function get_popup(data = null, popup_id = null) {
  let popup = null;
  popup_id = popup_id.replace("popup_", "");

  if (popup_id == "title") {
    data = globals.CHART_DIV.layout;
    let use_xaxis = data.xaxis ? "xaxis" : "xaxis2";
    let use_yaxis = data.yaxis ? "yaxis" : "yaxis2";

    let title = "title" in data && "text" in data.title ? data.title.text : "";
    let xaxis =
      "title" in data[use_xaxis] && "text" in data[use_xaxis].title
        ? data[use_xaxis].title.text
        : "";
    let yaxis =
      "title" in data[use_yaxis] && "text" in data[use_yaxis].title
        ? data[use_yaxis].title.text
        : "";

    globals.TITLE_DIV.innerHTML = `
        <div style="display:flex; flex-direction: column; gap: 6px;">
            <div>
            <label for="title_text">Title:</label>
            <input id="title_text" type="text" value="${title}"></input>
            </div>
            <div>
            <label for="title_xaxis">X axis:</label>
            <input id="title_xaxis" type="text" value="${xaxis}"></input>
            </div>
            <div>
            <label for="title_yaxis">Y axis:</label>
            <input id="title_yaxis" type="text" value="${yaxis}"></input>
            </div>
        </div>

        <div style="float: right; margin-top: 20px;">
        <button class="_btn-tertiary" id="title_cancel" onclick="closePopup()">Cancel</button>
        <button class="_btn" id="title_submit" onclick="on_submit('title')">Submit</button>
        </div>
        `;

    // when opening the popup, we make sure to focus on the title input
    globals.TITLE_DIV.style.display = "inline-block";
    globals.TITLE_DIV.querySelector("#title_text").focus();
    popup = globals.TITLE_DIV;
  } else if (popup_id == "text") {
    let has_annotation = false;
    if (data == undefined) {
      data = {
        text: "",
        font: {
          color: "#0088CC",
          size: 18,
        },
        bordercolor: "#822661",
      };
    } else {
      has_annotation = true;
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
        <textarea id="addtext_textarea" style="width: 100%; max-width: 100%; max-height: 200px; margin-top: 8px;" rows="4" cols="50" value="${
          data.text
        }"
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
            <input style="width: 45px;" type="number" id="addtext_size" value="${
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
      <button onclick="navigator.clipboard.writeText('${data.url}')" style="margin-top: 10px;" class="_btn">Copy to clipboard</button>
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
    data = {
      title: globals.TITLE_DIV.querySelector("#title_text").value,
      xaxis: globals.TITLE_DIV.querySelector("#title_xaxis").value,
      yaxis: globals.TITLE_DIV.querySelector("#title_yaxis").value,
    };
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
    console.log(data);
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
      };
    } else {
      data = {
        x: globals.CSV_DIV.querySelector("#csv_x").value,
        y: globals.CSV_DIV.querySelector("#csv_y").value,
        color: globals.CSV_DIV.querySelector("#csv_color").value,
      };
      console.log(data);
    }
    data.name = globals.CSV_DIV.querySelector("#csv_name").value;
    data.file = globals.CSV_DIV.querySelector("#csv_file");
    data.trace_type = trace_type;
  }
  return data;
}

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
    let yaxis = gd.layout.yaxis ? "yaxis" : "yaxis2";
    let xaxis = gd.layout.xaxis ? "xaxis" : "xaxis2";
    document.getElementById("title").innerHTML = popup_data.title;
    let to_update = { title: popup_data.title };
    to_update[xaxis + ".title"] = popup_data.xaxis;
    to_update[yaxis + ".title"] = popup_data.yaxis;
    to_update[yaxis + ".type"] = "linear";

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
        main_trace.showlegend = true;

        let yaxis_id = main_trace.yaxis;

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
          };
        } else {
          let yaxis;

          if (globals.csv_yaxis_id == null) {
            let yaxes = Object.keys(gd.layout)
              .filter((k) => k.startsWith("yaxis"))
              .map((k) => gd.layout[k].title);

            yaxis = `y${yaxes.length + 1}`;
            yaxis_id = `yaxis${yaxes.length + 1}`;

            globals.csv_yaxis_id = yaxis_id;
            globals.csv_yaxis = yaxis;
            gd.layout.margin.r -= 20;
            gd.layout.showlegend = true;
          }

          trace = {
            x: data.map(function (row) {
              return row[popup_data.x];
            }),
            y: data.map(function (row) {
              return (
                (row[popup_data.y] - data[0][popup_data.y]) /
                data[0][popup_data.y]
              );
            }),
            type: popup_data.trace_type,
            mode: "lines",
            name: popup_data.name,
            line: { color: popup_data.color },
            showlegend: true,
            connectgaps: true,
            xaxis: main_trace.xaxis,
            yaxis: globals.csv_yaxis,
          };

          if (globals.added_traces.length == 0) {
            gd.layout[yaxis_id] = {
              overlaying: "y",
              side: "left",
              title: {
                text: "% Change",
                font: {
                  size: 14,
                },
                standoff: 0,
              },
              tickfont: { size: 14 },
              ticksuffix: "     ",
              tickformat: ".0%",
              tickpadding: 5,
              showgrid: false,
              showline: false,
              showticklabels: true,
              zeroline: false,
              anchor: "x",
              type: "linear",
              autorange: true,
            };
            if (globals.cmd_src_idx != null) {
              gd.layout.annotations[globals.cmd_src_idx].xshift -= 15;
            }
          }
        }

        console.log(trace);

        globals.added_traces.push(trace.name);

        Plotly.addTraces(gd, trace);

        gd.layout[globals.csv_yaxis_id].type = "linear";
        Plotly.react(gd, gd.data, gd.layout);

        // We empty the fields and innerHTML after the plot is made
        globals.CSV_DIV.querySelector("#csv_colors").innerHTML = "";
        globals.CSV_DIV.querySelector("#csv_columns").innerHTML = "";

        globals.CSV_DIV.querySelectorAll("input").forEach(function (input) {
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
