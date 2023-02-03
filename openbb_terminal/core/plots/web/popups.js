function get_popup(data = null, popup_id = null) {
  let popup = null;
  popup_id = popup_id.replace("popup_", "");

  if (popup_id == "title") {
    data = globals.chartDiv.layout;
    let title = "title" in data && "text" in data.title ? data.title.text : "";
    let xaxis =
      "title" in data.xaxis && "text" in data.xaxis.title
        ? data.xaxis.title.text
        : "";
    let yaxis =
      "title" in data.yaxis && "text" in data.yaxis.title
        ? data.yaxis.title.text
        : "";

    TITLE_DIV.innerHTML = `
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
    TITLE_DIV.style.display = "inline-block";
    TITLE_DIV.querySelector("#title_text").focus();
    popup = TITLE_DIV;
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
      TEXT_DIV.querySelector("#addtext_above") == null
        ? "above"
        : TEXT_DIV.querySelector("#addtext_above").checked
        ? "above"
        : "below";

    TEXT_DIV.innerHTML = `
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
      TEXT_DIV.innerHTML += `
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
      TEXT_DIV.innerHTML += `
      <div style="float: right; margin-top: 20px;">
             <button class="_btn-tertiary" id="addtext_cancel" onclick="closePopup()">Cancel</button>
            <button class="_btn" id="addtext_submit" onclick="on_submit('text')">Submit</button>
    </div>
            `;

      if (TEXT_DIV.querySelector("#addtext_annotation") != null) {
        TEXT_DIV.querySelector("#addtext_annotation").remove();
      }
    }

    // when opening the popup, we make sure to focus on the textarea
    TEXT_DIV.style.display = "inline-block";
    TEXT_DIV.querySelector("#addtext_textarea").focus();
    popup = TEXT_DIV;
  } else if (popup_id == "csv") {
    CSV_DIV.style.display = "inline-block";
    popup = CSV_DIV;
    console.log("csv");
  } else if (popup_id == "upload") {
    TEXT_DIV.style.display = "inline-block";
    TEXT_DIV.innerHTML = `
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
    popup = TEXT_DIV;
    console.log("upload");
  }

  let popup_divs = [TITLE_DIV, TEXT_DIV, CSV_DIV];
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
      title: TITLE_DIV.querySelector("#title_text").value,
      xaxis: TITLE_DIV.querySelector("#title_xaxis").value,
      yaxis: TITLE_DIV.querySelector("#title_yaxis").value,
    };
  } else if (popup_id == "text") {
    data = {
      text: TEXT_DIV.querySelector("#addtext_textarea").value,
      color: TEXT_DIV.querySelector("#addtext_color").value,
      size: TEXT_DIV.querySelector("#addtext_size").value,
      yanchor: TEXT_DIV.querySelector("#addtext_above").checked
        ? "above"
        : "below",
      bordercolor: TEXT_DIV.querySelector("#addtext_border").value,
    };
    if (TEXT_DIV.querySelector("#addtext_annotation") != null) {
      data.annotation = JSON.parse(
        TEXT_DIV.querySelector("#addtext_annotation").value
      );
    }

    // we replace \n with <br> so that line breaks are displayed properly on the graph
    data.text = data.text.replace(/\n/g, "<br>");
    console.log(data);
  } else if (popup_id == "csv") {
    let trace_type = CSV_DIV.querySelector("#csv_trace_type").value;
    if (trace_type == "candlestick") {
      data = {
        x: CSV_DIV.querySelector("#csv_x").value,
        open: CSV_DIV.querySelector("#csv_open").value,
        high: CSV_DIV.querySelector("#csv_high").value,
        low: CSV_DIV.querySelector("#csv_low").value,
        close: CSV_DIV.querySelector("#csv_close").value,
        increasing: CSV_DIV.querySelector("#csv_increasing").value,
        decreasing: CSV_DIV.querySelector("#csv_decreasing").value,
      };
    } else {
      data = {
        x: CSV_DIV.querySelector("#csv_x").value,
        y: CSV_DIV.querySelector("#csv_y").value,
        color: CSV_DIV.querySelector("#csv_color").value,
      };
      console.log(data);
    }
    data.name = CSV_DIV.querySelector("#csv_name").value;
    data.file = CSV_DIV.querySelector("#csv_file");
    data.trace_type = trace_type;
  }
  return data;
}

function on_submit(popup_id, on_annotation = null) {
  // popup_id is either 'title', 'text', or 'csv' (for now)
  // and is used to determine which popup to get data from
  let popup_data = get_popup_data(popup_id);
  let gd = globals.chartDiv;
  Plotly.relayout(gd, "hovermode", "closest");

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
        Plotly.relayout(gd, "hovermode", "x");
      });

      let clickHandler = function (eventData) {
        let x = eventData.points[0].x;
        let yaxis = eventData.points[0].data.yaxis;
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
        Plotly.relayout(gd, "hovermode", "x");
      };

      Plotly.relayout(gd, { dragmode: "select" });
      gd.on("plotly_click", clickHandler);
    } else {
      let textarea = TEXT_DIV.querySelector("#addtext_textarea");
      document.getElementById("popup_textarea_warning").style.display = "block";
      textarea.style.border = "1px solid red";
      textarea.focus();

      TEXT_DIV.style.display = "inline-block";
      return;
    }
  } else if (popup_id == "title") {
    Plotly.relayout(gd, {
      title: popup_data.title,
      "xaxis.title": popup_data.xaxis,
      "yaxis.title": popup_data.yaxis,
      "yaxis.type": "linear",
    });
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
          };
        } else {
          trace = {
            x: data.map(function (row) {
              return row[popup_data.x];
            }),
            y: data.map(function (row) {
              return row[popup_data.y];
            }),
            type: popup_data.trace_type,
            mode: "lines",
            name: popup_data.name,
            line: { color: popup_data.color },
            xaxis: main_trace.xaxis,
            yaxis: main_trace.yaxis,
            connectgaps: true,
          };
        }

        Plotly.addTraces(gd, trace);
        Plotly.relayout(gd, { "yaxis.type": "linear" });
        Plotly.react(gd, gd.data, gd.layout);

        // We empty the fields and innerHTML after the plot is made
        CSV_DIV.querySelector("#csv_colors").innerHTML = "";
        CSV_DIV.querySelector("#csv_columns").innerHTML = "";

        CSV_DIV.querySelectorAll("input").forEach(function (input) {
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
  let gd = globals.chartDiv;
  closePopup();

  if (popup_id == "text") {
    let annotation = JSON.parse(
      TEXT_DIV.querySelector("#addtext_annotation").value
    );
    gd.layout.annotations.splice(gd.layout.annotations.indexOf(annotation), 1);

    Plotly.react(gd, gd.data, gd.layout);
    Plotly.relayout(gd, "dragmode", "pan");

    TEXT_DIV.style.display = "none";
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
