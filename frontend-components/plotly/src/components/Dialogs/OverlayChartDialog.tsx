import { useState } from "react";
import CommonDialog, { styleDialog } from "../Dialogs/CommonDialog";

const reader = new FileReader();

const layout_defaults = {
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

export default function OverlayChartDialog({
  open,
  close,
  setLoading,
  addOverlay,
  plotlyData,
}: {
  open: boolean;
  close: () => void;
  setLoading: (loading: boolean) => void;
  addOverlay: (data: any) => void;
  plotlyData: any;
}) {
  const [traceType, setTraceType] = useState("scatter");
  const [traceColor, setTraceColor] = useState("#FFDD00");
  const [increasingColor, setIncreasingColor] = useState("#00ACFF");
  const [decreasingColor, setDecreasingColor] = useState("#FF0000");
  const [traceName, setTraceName] = useState("");
  const [csvData, setCsvData] = useState<any[]>([]);
  const [csvColumns, setCsvColumns] = useState<string[]>([]);
  const [yaxisOptions, setYaxisOptions] = useState<any>({});
  const optionIds = ["x", "open", "high", "low", "close"];

  const traceTypes: any = {
    scatter: "Scatter (Line)",
    candlestick: "Candlestick",
    bar: "Bar",
  };

  const [options, setOptions] = useState<any>({});

  function onClose() {
    close();
    setTraceType("scatter");
    setTraceName("");
    setCsvData([]);
    setCsvColumns([]);
    setOptions({});
  }

  function onSubmit() {
    if (csvData.length === 0) {
      document.getElementById("csv_file")?.focus();
      document
        .getElementById("csv_file")
        ?.style.setProperty("border", "1px solid red");
      document.getElementById("csv_file_warning")!.style.display = "block";
      return;
    }
    const newPlotydata = CSVonSubmit({
      csvData: csvData,
      plotlyData: plotlyData,
      yaxisOptions: yaxisOptions,
      traceType: traceType,
      traceColor: traceColor,
      traceName: traceName,
      options: options,
      increasingColor: increasingColor,
      decreasingColor: decreasingColor,
    });
    addOverlay(newPlotydata);
    onClose();
  }

  return (
    <CommonDialog
      title="Overlay Chart"
      description="Upload a CSV file to overlay a chart on the main chart."
      open={open}
      close={close}
    >
      <div id="popup_csv" className="popup_content">
        <div>
          <label htmlFor="csv_file">
            <b>CSV file:</b>
            <div
              id="csv_file_warning"
              className="popup_warning"
              style={{ marginLeft: "80px", marginBottom: "10px" }}
            >
              CSV file is required.
            </div>
          </label>
          <input
            onChange={(e) => {
              if (!e.target.files) {
                return;
              } else if (e.target.files[0].type !== "text/csv") {
                document.getElementById("csv_file")?.focus();
                document
                  .getElementById("csv_file")
                  ?.style.setProperty("border", "1px solid red");
                document.getElementById("csv_file_warning")!.style.display =
                  "block";
                return;
              }

              if (csvColumns.length > 0) {
                setCsvColumns([]);
                setOptions({});
                setTraceType("scatter");
              }

              reader.onload = (filebytes) => {
                if (
                  !filebytes.target?.result ||
                  typeof filebytes.target.result !== "string"
                ) {
                  return;
                }
                const lines = filebytes.target.result
                  .split("\n")
                  .map((x) => x.replace(/\r/g, ""));

                const headers = lines[0].split(",");
                const headers_lower = headers.map((x) =>
                  x.trim().toLowerCase(),
                );

                const updateOptions: { [key: string]: any } = {};

                if (headers.length > 1) {
                  updateOptions.x = headers[0];
                  updateOptions.y = headers[1];
                }

                for (let i = 0; i < optionIds.length; i++) {
                  if (headers_lower.includes(optionIds[i])) {
                    updateOptions[optionIds[i]] =
                      headers[headers_lower.indexOf(optionIds[i])];
                  } else if (
                    optionIds[i] === "x" &&
                    headers_lower.includes("date")
                  ) {
                    updateOptions[optionIds[i]] =
                      headers[headers_lower.indexOf("date")];
                  }
                }

                const candle_cols = ["open", "high", "low", "close"];
                const candle_cols_present = candle_cols.every((x) =>
                  headers_lower.includes(x),
                );
                if (candle_cols_present) {
                  setTraceType("candlestick");
                } else if (headers_lower.length >= 5) {
                  candle_cols.forEach((x) => {
                    updateOptions[x] = headers[candle_cols.indexOf(x) + 1];
                  });
                }

                if (headers_lower.includes("close")) {
                  setOptions({
                    ...options,
                    y: headers[headers_lower.indexOf("close")],
                  });
                  updateOptions.y = headers[headers_lower.indexOf("close")];
                }

                const data = [];

                for (let i = 1; i < lines.length; i++) {
                  const obj = {};
                  const currentline = lines[i].split(",");
                  for (let j = 0; j < headers.length; j++) {
                    //@ts-ignore
                    obj[headers[j]] = currentline[j];
                  }
                  data.push(obj);
                }

                //@ts-ignore
                let filename = e.target.files[0].name.split(".")[0];

                try {
                  if (filename.includes("_")) {
                    const name_parts = filename
                      .replace(/_{2,}/g, "_")
                      .split("_");
                    const date_regex = new RegExp("^[0-9]{8}$");

                    if (name_parts.length > 2) {
                      // we check if the first 2 parts are date and time
                      if (date_regex.test(name_parts[0])) {
                        name_parts.splice(0, 2);
                      }
                      // we check if the last 2 parts are date and time
                      else if (
                        date_regex.test(name_parts[name_parts.length - 2])
                      ) {
                        name_parts.splice(name_parts.length - 2, 2);
                      }
                      filename = name_parts.join("_").replace(/openbb_/g, "");
                    }
                  }
                } catch (e) {
                  console.log(e);
                }

                setTraceName(filename);
                setOptions(updateOptions);
                setCsvColumns(headers);
                setCsvData(data);
              };
              reader.readAsText(e.target.files[0]);
            }}
            type="file"
            id="csv_file"
            accept=".csv"
            style={{ marginLeft: 10 }}
          />
        </div>
        <div style={{ marginTop: 15 }}>
          <label htmlFor="csv_trace_type">
            <b>Display data type:</b>
          </label>
          <select
            onChange={(e) => {
              setTraceType(e.target.value);
            }}
            id="csv_trace_type"
            style={styleDialog}
            defaultValue={traceTypes[traceType]}
          >
            {traceType && (
              <option key={traceType} value={traceType}>
                {traceTypes[traceType]}
              </option>
            )}
            {Object.keys(traceTypes).map(
              (x) =>
                traceType !== x && (
                  <option key={x} value={x}>
                    {traceTypes[x]}
                  </option>
                ),
            )}
          </select>
        </div>
        <div style={{ marginTop: 12 }}>
          <label htmlFor="csv_name">
            <b>Trace Name:</b>
          </label>
          <textarea
            id="csv_name"
            value={traceName}
            onChange={(e) => {
              setTraceName(e.target.value);
            }}
            style={{
              padding: "5px 2px 2px 5px",
              width: "100%",
              maxWidth: "100%",
              maxHeight: 200,
              marginTop: 2,
            }}
            rows={2}
            cols={20}
            placeholder="Enter a name to give this trace"
          />
        </div>
        {csvColumns.length > 0 && (
          <>
            {["scatter", "bar"].includes(traceType) && (
              <div
                style={{ marginTop: 15, marginBottom: 10 }}
                id="csv_columns"
                className="csv_column_container"
              >
                {["x", "y"].map((key) => (
                  <div
                    key={key}
                    style={{
                      marginTop: 10,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                    }}
                  >
                    <label htmlFor={`csv_${key}`} style={{ width: "100px" }}>
                      {key.toUpperCase()} Axis
                    </label>
                    <select
                      onChange={(e) => {
                        setOptions({
                          ...options,
                          [key]: e.target.value,
                        });
                      }}
                      id={`csv_${key}`}
                      style={{ width: "100%" }}
                      defaultValue={options[key]}
                    >
                      {csvColumns.map((column) => (
                        <option key={column} value={column}>
                          {column}
                        </option>
                      ))}
                    </select>
                  </div>
                ))}
              </div>
            )}
            {traceType === "candlestick" && (
              <div
                id="csv_columns"
                className="csv_column_container"
                style={{ marginTop: 15 }}
              >
                {["x", "open", "high", "low", "close"].map((key) => (
                  <div
                    key={key}
                    style={{
                      marginTop: 10,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                    }}
                  >
                    <label htmlFor={`csv_${key}`} style={{ width: "100px" }}>
                      {key.charAt(0).toUpperCase() + key.slice(1)}
                    </label>
                    <select
                      onChange={(e) => {
                        setOptions({
                          ...options,
                          [key]: e.target.value,
                        });
                      }}
                      id={`csv_${key}`}
                      style={{ width: "100%" }}
                      defaultValue={options[key]}
                    >
                      {csvColumns.map((column) => (
                        <option key={column} value={column}>
                          {column}
                        </option>
                      ))}
                    </select>
                  </div>
                ))}
              </div>
            )}
            <div style={{ marginTop: 20 }} id="csv_colors">
              {["scatter", "bar"].includes(traceType) && (
                <div>
                  <label htmlFor="csv_color">{`${traceType
                    .charAt(0)
                    .toUpperCase()}${traceType.slice(1)} color`}</label>
                  <input
                    type="color"
                    id="csv_color"
                    defaultValue="#FFDD00"
                    style={{ margin: "2px 2px 2px 10px" }}
                    onChange={(e) => {
                      console.log(e.target.value);
                      setTraceColor(e.target.value);
                    }}
                  />
                </div>
              )}
              {traceType === "candlestick" && (
                <>
                  <label htmlFor="csv_increasing">Increasing color</label>
                  <input
                    type="color"
                    id="csv_increasing"
                    defaultValue="#00ACFF"
                    style={{ margin: "2px 0px 2px 10px" }}
                    onChange={(e) => {
                      setIncreasingColor(e.target.value);
                    }}
                  />
                  <label htmlFor="csv_decreasing" style={{ marginLeft: 15 }}>
                    Decreasing color
                  </label>
                  <input
                    style={{ margin: "2px 0px 2px 10px" }}
                    type="color"
                    id="csv_decreasing"
                    defaultValue="#FF0000"
                    onChange={(e) => {
                      setDecreasingColor(e.target.value);
                    }}
                  />
                </>
              )}
            </div>
            <div style={{ marginTop: 20 }} id="csv_plot_yaxis_options">
              {traceType !== "candlestick" && (
                <>
                  <input
                    type="checkbox"
                    id="csv_percent_change"
                    name="csv_plot_yaxis_check"
                    style={{ marginBottom: 2 }}
                    onChange={(e) => {
                      setYaxisOptions({
                        ...yaxisOptions,
                        percentChange: e.target.checked,
                        sameYaxis: false,
                      });
                    }}
                    checked={
                      !yaxisOptions.sameYaxis && yaxisOptions.percentChange
                    }
                  />
                  <label htmlFor="csv_percent_change" style={{ marginLeft: 5 }}>
                    Plot as percent change from first value
                  </label>
                  <br />
                </>
              )}
              <input
                style={{ marginTop: 2 }}
                type="checkbox"
                id="csv_same_yaxis"
                name="csv_plot_yaxis_check"
                onChange={(e) => {
                  setYaxisOptions({
                    ...yaxisOptions,
                    sameYaxis: e.target.checked,
                    percentChange: false,
                  });
                }}
                checked={!yaxisOptions.percentChange && yaxisOptions.sameYaxis}
              />
              <label htmlFor="csv_same_yaxis" style={{ marginLeft: 5 }}>
                Share Y-axis
              </label>

              {traceType === "bar" && (
                <div style={{ marginTop: 2 }} id="csv_bar_orientation">
                  <input
                    type="checkbox"
                    id="csv_bar_horizontal"
                    onChange={(e) => {
                      setOptions({
                        ...options,
                        orientation: e.target.checked ? "h" : "v",
                      });
                    }}
                  />
                  <label htmlFor="csv_bar_horizontal" style={{ marginLeft: 5 }}>
                    Plot horizontally
                  </label>
                </div>
              )}
            </div>
          </>
        )}

        <br />
        <div style={{ float: "right", marginTop: 20 }}>
          <button className="_btn-tertiary" id="csv_cancel" onClick={onClose}>
            Cancel
          </button>
          <button className="_btn" id="csv_submit" onClick={onSubmit}>
            Submit
          </button>
        </div>
      </div>
    </CommonDialog>
  );
}

export function CSVonSubmit({
  csvData,
  plotlyData,
  yaxisOptions,
  traceType,
  traceColor,
  traceName,
  options,
  increasingColor,
  decreasingColor,
}: {
  csvData: any[];
  plotlyData: any;
  yaxisOptions: any;
  traceType: string;
  traceColor: string;
  traceName: string;
  options: any;
  increasingColor: string;
  decreasingColor: string;
}) {
  console.log("options", options);
  const main_trace = plotlyData.data[0] || {};
  if (main_trace.xaxis === undefined) {
    main_trace.xaxis = "x";
  }
  if (main_trace.yaxis === undefined) {
    main_trace.yaxis = "y";
  }
  let yaxis_id = main_trace.yaxis;
  let yaxis: string;

  const left_yaxis_ticks = Object.keys(plotlyData.layout)
    .filter((k) => k.startsWith("yaxis"))
    .map((k) => plotlyData.layout[k])
    .filter(
      (yaxis) =>
        yaxis.side === "left" &&
        (yaxis.overlaying === "y" ||
          (yaxis.fixedrange !== undefined && yaxis.fixedrange === true)),
    ).length;

  const ticksuffix = left_yaxis_ticks > 0 ? "     " : "";

  if (yaxisOptions.sameYaxis !== true) {
    const yaxes = Object.keys(plotlyData.layout)
      .filter((k) => k.startsWith("yaxis"))
      .map((k) => plotlyData.layout[k]);

    yaxis = `y${yaxes.length + 1}`;
    yaxis_id = `yaxis${yaxes.length + 1}`;
    plotlyData.layout[yaxis_id] = {
      ...layout_defaults,
      title: {
        text: traceName,
        font: {
          size: 14,
        },
        standoff: 0,
      },
      ticksuffix: ticksuffix,
      layer: "below traces",
    };
  } else {
    // Plot on the same yaxis
    yaxis = main_trace.yaxis.replace("yaxis", "y");
  }

  const traceBase: any = {
    type: traceType,
    name: traceName,
    showlegend: true,
    yaxis: yaxis,
  };

  let trace: any = {};

  if (["scatter", "bar"].includes(traceType)) {
    if (!csvData || csvData.length === 0) return plotlyData;
    const non_null = csvData.findIndex(
      (x: any) => x[options.y] !== null && x[options.y] !== 0,
    );

    if (non_null === -1) {
      return plotlyData;
    }

    const scatter_data: { [key: string]: any[] } = {
      x: [],
      y: [],
      customdata: [],
    };

    csvData.forEach((row: any) => {
      let y = row[options.y];
      scatter_data.customdata.push(y);
      if (
        yaxisOptions.percentChange &&
        (traceType === "scatter" || traceType === "line")
      ) {
        y =
          (row[options.y] - csvData[non_null][options.y]) /
          csvData[non_null][options.y];
      }
      scatter_data.x.push(row[options.x]);
      scatter_data.y.push(y);
    });

    trace = {
      ...traceBase,
      x: scatter_data.x,
      y: scatter_data.y,
      customdata: scatter_data.customdata,
      hovertemplate: "%{customdata:.2f}",
      connectgaps: true,
      marker: { color: traceColor },
    };

    if (traceType === "bar") {
      trace.orientation = options.orientation;
      trace.marker.opacity = 0.7;
      trace.connectgaps = undefined;
      trace.hovertemplate = undefined;
      trace.customdata = undefined;
    }
  } else if (traceType === "candlestick") {
    const candlestick_data: { [key: string]: any[] } = {
      x: [],
      open: [],
      high: [],
      low: [],
      close: [],
    };

    csvData.forEach((row: any) => {
      candlestick_data.x.push(row[options.x]);
      candlestick_data.open.push(row[options.open]);
      candlestick_data.high.push(row[options.high]);
      candlestick_data.low.push(row[options.low]);
      candlestick_data.close.push(row[options.close]);
    });

    trace = {
      ...traceBase,
      x: candlestick_data.x,
      open: candlestick_data.open,
      high: candlestick_data.high,
      low: candlestick_data.low,
      close: candlestick_data.close,
      increasing: {
        line: { color: increasingColor, width: 0.8 },
        fillcolor: increasingColor,
      },
      decreasing: {
        line: { color: decreasingColor, width: 0.8 },
        fillcolor: decreasingColor,
      },
    };
  }

  return {
    ...plotlyData,
    data: [...plotlyData.data, trace],
  };
}
