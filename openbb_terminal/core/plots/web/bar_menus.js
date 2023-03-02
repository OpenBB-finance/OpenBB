// Custom Menu functions for Plotly charts

function autoScaling(eventdata, graphs) {
  try {
    if (eventdata["xaxis.range[0]"] != undefined) {
      let log_scale = true
        ? graphs.layout.yaxis != undefined && graphs.layout.yaxis.type == "log"
        : false;

      let secondary_y = true
        ? graphs.layout.yaxis2 != undefined &&
          graphs.layout.yaxis2.overlaying == "y"
        : false;

      let x_min = eventdata["xaxis.range[0]"];
      let x_max = eventdata["xaxis.range[1]"];

      let y_min, y_max;
      let y_done = [];

      for (let trace of graphs.data) {
        let yaxis = !trace.yaxis
          ? "yaxis"
          : "yaxis" + trace.yaxis.replace("y", "");

        if (trace.x != undefined) {
          if (y_done.indexOf(yaxis) == -1) {
            y_done.push(yaxis);
          } else {
            continue;
          }

          let x = trace.x;
          let y_low, y_high;

          if (trace.close != undefined) {
            y_high = trace.high;
            y_low = trace.low;
          }

          let y = y_low ? y_low : trace.y;

          if (log_scale) {
            y = y.map(Math.log10);
            if (y_high != undefined) {
              y_high = y_high.map(Math.log10);
            }
          }
          for (let i = 0; i < x.length; i++) {
            if (x[i] >= x_min && x[i] <= x_max) {
              if (y_min == undefined || y_min > y[i]) {
                y_min = y[i];
              }

              let y_high_value = y_high ? y_high[i] : y[i];
              if (y_max == undefined || y_max < y_high_value) {
                y_max = y_high_value;
              }
            }
          }
        }

        if (y_min != undefined && y_max != undefined) {
          if (yaxis != "yaxis" && log_scale) {
            y_min = Math.pow(10, y_min);
            y_max = Math.pow(10, y_max);
          }

          let y_range = y_max - y_min;

          if (yaxis == "yaxis" && graphs.layout.yaxis.range[0] != 0) {
            y_min -= y_range * 0.15;
          }
          y_max += y_range * 0.15;

          if (yaxis == "yaxis" && secondary_y) {
            secondary_y = [y_min, y_max];
          }

          if (yaxis == "yaxis2" && secondary_y) {
            let y2_max = secondary_y[1] - secondary_y[0] * 1.5;
            y_min = 0;
            y_max = secondary_y[1] - secondary_y[0] * 1.5;

            if ((secondary_y[1] - y2_max) / secondary_y[1] > 0.5) {
              y_max = secondary_y[0] * 1.2;
            }
            if ((secondary_y[0] - y2_max) / secondary_y[0] > 0.5) {
              y_max = secondary_y[1] * 1.2;
            }
          }

          Plotly.relayout(globals.chartDiv, yaxis + ".range", [y_min, y_max]);
        }
      }
    }
  } catch (e) {
    console.log(`Error in AutoScaling: ${e}`);
  }
}

function changeColor() {
  if (!globals.color_picker) {
    let color_picker = document.getElementById("changecolor");
    globals.color_picker = color_picker;

    color_picker.style.display = "block";
    color_picker.style.width = null;
    dragElement(color_picker);

    function dragElement(elmnt) {
      let pos1 = 0,
        pos2 = 0,
        pos3 = 0,
        pos4 = 0;
      if (document.getElementById(elmnt.id + "_header")) {
        // if present, the header is where you move the DIV from:
        document.getElementById(elmnt.id + "_header").onmousedown =
          dragMouseDown;
      } else {
        // otherwise, move the DIV from anywhere inside the DIV:
        elmnt.onmousedown = dragMouseDown;
      }

      function dragMouseDown(e) {
        e = e || window.event;
        e.preventDefault();
        // get the mouse cursor position at startup:
        pos3 = e.clientX;
        pos4 = e.clientY;
        document.onmouseup = closeDragElement;
        // call a function whenever the cursor moves:
        document.onmousemove = elementDrag;
      }

      function elementDrag(e) {
        e = e || window.event;
        e.preventDefault();
        // calculate the new cursor position:
        pos1 = pos3 - e.clientX;
        pos2 = pos4 - e.clientY;
        pos3 = e.clientX;
        pos4 = e.clientY;
        // set the element's new position:
        elmnt.style.top = elmnt.offsetTop - pos2 + "px";
        elmnt.style.left = elmnt.offsetLeft - pos1 + "px";
      }

      function closeDragElement() {
        // stop moving when mouse button is released:
        document.onmouseup = null;
        document.onmousemove = null;
      }
    }
  } else {
    globals.color_picker.style.display = "none";
    globals.color_picker = null;
  }
}

function downloadImage() {
  const loader = document.getElementById("loader");
  loader.classList.add("show");
  Plotly.toImage(globals.chartDiv, {
    format: "png",
    height: 627,
    width: 1200,
  })
    .then(function (url) {
      let data = {
        image: url,
        title: globals.title,
        description: "Check out this chart from OpenBB",
      };

      fetch("https://uppy-self.vercel.app/api/upload-image", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      })
        .then(function (response) {
          return response.json();
        })
        .then(function (data) {
          const { url, id } = data;
          loader.classList.remove("show");
          openPopup("popup_upload", { url });
        })
        .catch(function (err) {
          console.log(err);
          loader.classList.remove("show");
        });
    })
    .catch(function (err) {
      console.log(err);
      loader.classList.remove("show");
    });
}

function downloadData(gd) {
  let data = gd.data;
  let candlestick = false;
  let csv = undefined;

  data.forEach(function (trace) {
    // check if candlestick
    if (trace.type == "candlestick") {
      candlestick = true;
      return;
    }
  });

  let xaxis =
    "title" in gd.layout["xaxis"] &&
    gd.layout["xaxis"]["title"]["text"] != undefined
      ? gd.layout["xaxis"]["title"]["text"]
      : "x";

  let yaxis =
    "title" in gd.layout["yaxis"] &&
    gd.layout["yaxis"]["title"]["text"] != undefined
      ? gd.layout["yaxis"]["title"]["text"]
      : "y";

  if (candlestick) {
    csv = "Date,Open,High,Low,Close\r";
    data.forEach(function (trace) {
      if (trace.type == "candlestick") {
        let x = trace.x;
        let open = trace.open;
        let high = trace.high;
        let low = trace.low;
        let close = trace.close;

        for (let i = 0; i < x.length; i++) {
          csv += `${x[i]},${open[i]},${high[i]},${low[i]},${close[i]}\r`;
        }
      }
    });
  } else {
    let traces = 0;
    data.forEach(function (trace) {
      if (trace.type == "scatter") {
        traces++;
      }
    });

    if (traces == 1) {
      csv = `${xaxis},${yaxis}\r`;
      data.forEach(function (trace) {
        if (trace.type == "scatter") {
          let x = trace.x;
          let y = trace.y;

          for (let i = 0; i < x.length; i++) {
            csv += `${x[i]},${y[i]}\r`;
          }
        }
      });
    } else if (traces > 1) {
      csv = `${xaxis},`;
      data.forEach(function (trace) {
        if (trace.type == "scatter") {
          csv += `${trace.name},`;
        }
      });
      csv += "\r";

      let x = data[0].x;
      for (let i = 0; i < x.length; i++) {
        csv += `${x[i]},`;
        data.forEach(function (trace) {
          if (trace.type == "scatter") {
            csv += `${trace.y[i]},`;
          }
        });
        csv += "\r";
      }
    } else {
      return;
    }
  }

  let filename = openbbFilename(gd, true);
  let blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  if (navigator.msSaveBlob) {
    // IE 10+
    navigator.msSaveBlob(blob, filename);
  } else {
    let link = window.document.createElement("a");
    if (link.download !== undefined) {
      // feature detection
      // Browsers that support HTML5 download attribute
      let url = URL.createObjectURL(blob);
      link.setAttribute("href", url);
      link.setAttribute("download", filename);
      link.style.visibility = "hidden";
      window.document.body.appendChild(link);
      link.click();
      window.document.body.removeChild(link);
    }
  }
}
