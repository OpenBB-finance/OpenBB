// Custom Menu functions for Plotly charts

function autoScaling(eventdata, graphs) {
  try {
    if (eventdata["xaxis.range[0]"] != undefined) {
      const x_min = eventdata["xaxis.range[0]"];
      const x_max = eventdata["xaxis.range[1]"];
      let to_update = {};
      let y_min, y_max;

      const YaxisData = graphs.data.filter((trace) => trace.yaxis != undefined);
      const yaxis_unique = [
        ...new Set(
          YaxisData.map(
            (trace) =>
              trace.yaxis || trace.y != undefined || trace.type == "candlestick"
          )
        ),
      ];

      const get_all_yaxis_traces = (yaxis) => {
        return graphs.data.filter(
          (trace) =>
            trace.yaxis == yaxis && (trace.y || trace.type == "candlestick")
        );
      };

      yaxis_unique.forEach((unique) => {
        if (typeof unique != "string") {
          return;
        }
        let yaxis = "yaxis" + unique.replace("y", "");
        let y_candle = [];
        let y_values = [];
        let log_scale = graphs.layout[yaxis].type == "log";

        get_all_yaxis_traces(unique).forEach((trace2) => {
          let x = trace2.x;
          log_scale = graphs.layout[yaxis].type == "log";

          let y = trace2.y != undefined ? trace2.y : [];
          let y_low = trace2.type == "candlestick" ? trace2.low : [];
          let y_high = trace2.type == "candlestick" ? trace2.high : [];

          if (log_scale) {
            y = y.map(Math.log10);
            if (trace2.type == "candlestick") {
              y_low = trace2.low.map(Math.log10);
              y_high = trace2.high.map(Math.log10);
            }
          }

          let yx_values = x.map((x, i) => {
            let out = null;
            if (x >= x_min && x <= x_max) {
              if (trace2.y != undefined) {
                console.log(trace2.name, trace2.type, trace2.yaxis);
                out = y[i];
              }
              if (trace2.type == "candlestick") {
                y_candle.push(y_low[i]);
                y_candle.push(y_high[i]);
              }
            }
            return out;
          });

          y_values = y_values.concat(yx_values);
        });

        y_values = y_values.filter((y2) => y2 != undefined && y2 != null);
        y_min = Math.min(...y_values);
        y_max = Math.max(...y_values);

        if (y_candle.length > 0) {
          y_candle = y_candle.filter((y2) => y2 != undefined && y2 != null);
          y_min = Math.min(...y_candle);
          y_max = Math.max(...y_candle);
        }

        let org_y_max = y_max;
        let is_volume =
          graphs.layout[yaxis].fixedrange != undefined &&
          graphs.layout[yaxis].fixedrange == true;

        if (y_min != undefined && y_max != undefined) {
          let y_range = y_max - y_min;
          let y_mult = 0.15;
          if (y_candle.length > 0) {
            y_mult = 0.3;
          }

          y_min -= y_range * y_mult;
          y_max += y_range * y_mult;

          if (is_volume) {
            if (graphs.layout[yaxis].tickvals != undefined) {
              const range_x = 7;
              let volume_ticks = org_y_max;
              let round_digits = -3;
              let first_val = Math.round(volume_ticks * 0.2, round_digits);
              let x_zipped = [2, 5, 6, 7, 8, 9, 10];
              let y_zipped = [1, 4, 5, 6, 7, 8, 9];

              for (let i = 0; i < x_zipped.length; i++) {
                if (String(volume_ticks).length > x_zipped[i]) {
                  round_digits = -y_zipped[i];
                  first_val = Math.round(volume_ticks * 0.2, round_digits);
                }
              }
              let tickvals = [
                Math.floor(first_val),
                Math.floor(first_val * 2),
                Math.floor(first_val * 3),
                Math.floor(first_val * 4),
              ];
              let volume_range = [0, Math.floor(volume_ticks * range_x)];

              to_update[yaxis + ".tickvals"] = tickvals;
              to_update[yaxis + ".range"] = volume_range;
              to_update[yaxis + ".tickformat"] = ".2s";
              return;
            }
            y_min = 0;
            y_max = graphs.layout[yaxis].range[1];
          }
          to_update[yaxis + ".range"] = [y_min, y_max];
        }
      });
      Plotly.update(graphs, {}, to_update);
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

function uploadImage() {
  const loader = document.getElementById("loader");
  loader.classList.add("show");
  Plotly.toImage(globals.CHART_DIV, {
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

function downloadImage(filename, extension) {
  const loader = document.getElementById("loader");
  loader.classList.add("show");

  let imageDownload = undefined;

  if (extension == "png") {
    imageDownload = domtoimage.toPng;
  } else if (extension == "jpeg") {
    imageDownload = domtoimage.toJpeg;
    // } else if (extension == "svg") {
    //   imageDownload = domtoimage.toSvg;
  } else if (["svg", "pdf"].includes(extension)) {
    Plotly.downloadImage(globals.CHART_DIV, {
      format: "svg",
      height: globals.CHART_DIV.clientHeight,
      width: globals.CHART_DIV.clientWidth,
      filename: filename,
    });
    return;
  } else {
    console.log("Invalid extension");
    return;
  }
  imageDownload(document.getElementById("openbb_container"))
    .then(function (dataUrl) {
      downloadURI(dataUrl, filename + "." + extension);
      loader.classList.remove("show");
    })
    .catch(function (error) {
      console.error("oops, something went wrong!", error);
      loader.classList.remove("show");
      hideModebar();
    });
}

function downloadURI(uri, name) {
  let link = document.createElement("a");
  link.download = name;
  link.href = uri;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
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
    csv = "Date,Open,High,Low,Close\n";
    data.forEach(function (trace) {
      if (trace.type == "candlestick") {
        let x = trace.x;
        let open = trace.open;
        let high = trace.high;
        let low = trace.low;
        let close = trace.close;

        for (let i = 0; i < x.length; i++) {
          csv += `${x[i]},${open[i]},${high[i]},${low[i]},${close[i]}\n`;
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
      csv = `${data[0].name},${xaxis},${yaxis}\n`;
      data.forEach(function (trace) {
        if (trace.type == "scatter") {
          let x = trace.x;
          let y = trace.y;

          for (let i = 0; i < x.length; i++) {
            csv += `${x[i]},${y[i]}\n`;
          }
        }
      });
    } else if (traces > 1) {
      csv = `${xaxis}`;
      data.forEach(function (trace) {
        if (trace.type == "scatter") {
          csv += `,${trace.name}`;
        }
      });
      csv += "\n";

      let x = data[0].x;
      for (let i = 0; i < x.length; i++) {
        csv += `${x[i]}`;
        data.forEach(function (trace) {
          if (trace.type == "scatter") {
            csv += `,${trace.y[i]}`;
          }
        });
        csv += "\n";
      }
    } else {
      return;
    }
  }

  let filename = globals.filename;
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
