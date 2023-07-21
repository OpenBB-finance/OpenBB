// @ts-nocheck
import clsx from "clsx";
import { debounce } from "lodash";
import * as Plotly from "plotly.js-dist-min";
import { Icons as PlotlyIcons } from "plotly.js-dist-min";
import { usePostHog } from "posthog-js/react";
import React, { useCallback, useEffect, useMemo, useState } from "react";
import createPlotlyComponent from "react-plotly.js/factory";
import { init_annotation } from "../utils/addAnnotation";
import { non_blocking, saveImage } from "../utils/utils";
import autoScaling, { isoDateRegex } from "./AutoScaling";
import ChangeColor from "./ChangeColor";
import { DARK_CHARTS_TEMPLATE, ICONS, LIGHT_CHARTS_TEMPLATE } from "./Config";
import AlertDialog from "./Dialogs/AlertDialog";
import DownloadFinishedDialog from "./Dialogs/DownloadFinishedDialog";
import OverlayChartDialog from "./Dialogs/OverlayChartDialog";
import TextChartDialog from "./Dialogs/TextChartDialog";
import TitleChartDialog from "./Dialogs/TitleChartDialog";
import { PlotConfig, hideModebar, ChartHotkeys } from "./PlotlyConfig";
import ResizeHandler from "./ResizeHandler";

const Plot = createPlotlyComponent(Plotly);
class PlotComponent extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      data: props.data,
      layout: props.layout,
      frames: props.frames,
      config: props.config,
      useResizeHandler: props.useResizeHandler,
      style: props.style,
      className: props.className,
      divId: props.divId,
      revision: props.revision,
      graphDiv: props.graphDiv,
      debug: props.debug,
      onInitialized: props.onInitialized,
    };
  }

  render() {
    return (
      <Plot
        data={this.state.data}
        layout={this.state.layout}
        frames={this.state.frames}
        config={this.state.config}
        useResizeHandler={this.state.useResizeHandler}
        style={this.state.style}
        className={this.state.className}
        divId={this.state.divId}
        revision={this.state.revision}
        graphDiv={this.state.graphDiv}
        debug={this.state.debug}
        onInitialized={this.state.onInitialized}
        onUpdate={(figure) => this.setState(figure)}
        onRelayout={(figure) => this.setState(figure)}
        onPurge={(figure) => this.setState(figure)}
      />
    );
  }
}

export const getXRange = (min: string, max: string) => {
  if (isoDateRegex.test(min.replace(" ", "T").split(".")[0])) {
    const check_min = new Date(min.replace(" ", "T").split(".")[0]);
    const check_max = new Date(max.replace(" ", "T").split(".")[0]);
    check_min.setSeconds(0);
    check_max.setSeconds(0);
    check_min.setMilliseconds(0);
    check_max.setMilliseconds(0);

    const multiplier =
      [5, 0, 1].includes(check_min.getDay()) ||
      [4, 5, 6].includes(check_max.getDay())
        ? 2
        : 0;

    const x0_min = new Date(check_min.getTime() - 86400000 * multiplier);
    const x1_max = new Date(check_max.getTime() + 86400000 * multiplier);

    const xrange = [x0_min.toISOString(), x1_max.toISOString()];
    return { x0_min, x1_max, xrange };
  }

  return { x0_min: min, x1_max: max, xrange: [min, max] };
};

function CreateDataXrange(figure: Figure, xrange?: any) {
  const new_figure = { ...figure };
  const data = new_figure.data;
  if (!xrange) {
    xrange = [
      data[0]?.x[data[0].x.length - 2000],
      data[0]?.x[data[0].x.length - 1],
    ];
  }
  const { x0_min, x1_max, range } = getXRange(xrange[0], xrange[1]);
  xrange = range;

  const new_data = [];
  data.forEach((trace) => {
    const new_trace = { ...trace };
    const data_keys = [
      "x",
      "y",
      "low",
      "high",
      "open",
      "close",
      "text",
      "customdata",
    ];
    const xaxis: any[] = trace.x ? trace.x : [];
    const chunks = [];
    for (let i = 0; i < xaxis.length; i++) {
      const xval = xaxis[i];

      if (isoDateRegex.test(xval)) {
        const x_time = new Date(xval).getTime();
        if (x_time >= x0_min.getTime() && x_time <= x1_max.getTime()) {
          chunks.push(i);
        }
      } else if (xval >= xrange[0] && xval <= xrange[1]) {
        chunks.push(i);
      }
    }
    data_keys.forEach((key) => {
      if (trace[key] !== undefined && Array.isArray(trace[key])) {
        new_trace[key] = trace[key].filter((_, i) => chunks.includes(i));
      }
    });
    const color_keys = ["marker", "line"];
    color_keys.forEach((key) => {
      if (trace[key]?.color && Array.isArray(trace[key].color)) {
        new_trace[key] = { ...trace[key] };
        new_trace[key].color = trace[key].color.filter((_, i) =>
          chunks.includes(i),
        );
      }
    });

    if (chunks.length > 0) new_data.push(new_trace);
  });

  if (new_data.length === 0)
    return {
      ...figure,
      layout: {
        ...figure.layout,
        xaxis: { ...figure.layout.xaxis, range: xrange },
      },
    };

  new_figure.layout.xaxis.range = xrange;
  new_figure.data = new_data;
  return new_figure;
}

async function DynamicLoad({
  event,
  figure,
}: {
  event?: any;
  figure: any;
}) {
  try {
    const XDATA = figure.data.filter(
      (trace) =>
        trace.x !== undefined && trace.x.length > 0 && trace.x[0] !== undefined,
    );

    if (XDATA.length === 0) return figure;
    // We get the xaxis range, if no event is passed, we get the last 2000 points
    const xaxis_range = event
      ? [event["xaxis.range[0]"], event["xaxis.range[1]"]]
      : [
          XDATA[0]?.x[XDATA[0].x.length - 2000],
          XDATA[0]?.x[XDATA[0].x.length - 1],
        ];

    figure = CreateDataXrange(figure, xaxis_range);

    return figure;
  } catch (e) {
    console.log("error", e);
  }
}

function formatDate(date) {
  const d = new Date(date);
  const month = `${d.getMonth() + 1}`.padStart(2, "0");
  const day = `${d.getDate()}`.padStart(2, "0");
  const year = d.getFullYear();
  const hour = `${d.getHours()}`.padStart(2, "0");
  const minute = `${d.getMinutes()}`.padStart(2, "0");
  const second = `${d.getSeconds()}`.padStart(2, "0");
  return `${year}-${month}-${day} ${hour}:${minute}:${second}`;
}

function Chart({
  json,
  date,
  cmd,
  title,
  globals,
  theme,
  info,
}: {
  // @ts-ignore
  json: Figure;
  date: Date;
  cmd: string;
  title: string;
  globals: any;
  theme: string;
  info?: any;
}) {
  const posthog = usePostHog();

  useEffect(() => {
    if (posthog) posthog.capture("chart", info);
  }, []);

  json.layout.width = undefined;
  json.layout.height = undefined;
  if (json.layout?.title?.text) {
    json.layout.title.text = "";
  }

  const [originalData, setOriginalData] = useState(json);
  const [barButtons, setModeBarButtons] = useState({});
  const [LogYaxis, setLogYaxis] = useState(false);
  const [chartTitle, setChartTitle] = useState(title);
  const [axesTitles, setAxesTitles] = useState({});
  const [plotLoaded, setPlotLoaded] = useState(false);
  const [modal, setModal] = useState({ name: "" });
  const [loading, setLoading] = useState(false);
  const [plotDiv, setPlotDiv] = useState(null);
  const [volumeBars, setVolumeBars] = useState({ old_nticks: {} });
  const [maximizePlot, setMaximizePlot] = useState(false);
  const [downloadFinished, setDownloadFinished] = useState(false);
  const [dateSliced, setDateSliced] = useState(false);

  const [plotData, setPlotDataState] = useState(originalData);
  const [annotations, setAnnotations] = useState([]);
  const [changeTheme, setChangeTheme] = useState(false);
  const [darkMode, setDarkMode] = useState(true);
  const [autoScale, setAutoScaling] = useState(false);
  const [changeColor, setChangeColor] = useState(false);
  const [colorActive, setColorActive] = useState(false);
  const [onAnnotationClick, setOnAnnotationClick] = useState({});
  const [ohlcAnnotation, setOhlcAnnotation] = useState([]);
  const [yaxisFixedRange, setYaxisFixedRange] = useState([]);

  function setPlotData(data: any) {
    data.layout.datarevision = data.layout.datarevision
      ? data.layout.datarevision + 1
      : 1;
    setPlotDataState(data);
    if (plotDiv && plotData) {
      Plotly.react(plotDiv, data.data, data.layout);
    }
  }

  const onClose = () => setModal({ name: "" });

  // @ts-ignore
  const onDeleteAnnotation = useCallback(
    (annotation) => {
      console.log("onDeleteAnnotation", annotation);
      const index = plotData?.layout?.annotations?.findIndex(
        (a: any) => a.text === annotation.text,
      );
      console.log("index", index);
      if (index > -1) {
        plotData?.layout?.annotations?.splice(index, 1);
        setPlotData({ ...plotData });
        setAnnotations(plotData?.layout?.annotations);
      }
    },
    [plotData],
  );

  // @ts-ignore
  const onAddAnnotation = useCallback(
    (data) => {
      init_annotation({
        plotData,
        popupData: data,
        setPlotData,
        setModal,
        setOnAnnotationClick,
        setAnnotations,
        onAnnotationClick,
        ohlcAnnotation,
        setOhlcAnnotation,
        annotations,
        plotDiv,
      });
    },
    [plotData, onAnnotationClick, ohlcAnnotation, annotations, plotDiv],
  );

  useEffect(() => {
    if (downloadFinished) {
      setModal({ name: "downloadFinished" });
      setDownloadFinished(false);
    }
  }, [downloadFinished]);

  useEffect(() => {
    if (axesTitles && Object.keys(axesTitles).length > 0) {
      Object.keys(axesTitles).forEach((k) => {
        plotData.layout[k].title = {
          ...(plotData.layout[k].title || {}),
          text: axesTitles[k],
        };
        plotData.layout[k].showticklabels = true;
      });
      setAxesTitles({});
    }
  }, [axesTitles]);

  function onChangeColor(color) {
    // updates the color of the last added shape
    // this function is called when the color picker is used
    // if there are no shapes, we remove the color picker
    const shapes = plotDiv.layout.shapes;
    if (!shapes || shapes.length === 0) {
      return;
    }
    // we change last added shape color
    const last_shape = shapes[shapes.length - 1];
    last_shape.line.color = color;
    Plotly.update(plotDiv, {}, { shapes: shapes });
  }

  function button_pressed(title, active = false) {
    // changes the style of the button when it is pressed
    // title is the title of the button
    // active is true if the button is active, false otherwise

    const button =
      barButtons[title] || document.querySelector(`[data-title="${title}"]`);
    if (!active) {
      button.style.border = "1px solid rgba(0, 151, 222, 1.0)";
      button.style.borderRadius = "5px";
      button.style.borderpadding = "5px";
      button.style.boxShadow = "0 0 5px rgba(0, 151, 222, 1.0)";
    } else {
      button.style.border = "transparent";
      button.style.boxShadow = "none";
    }
    setModeBarButtons({ ...barButtons, [title]: button });
  }

  const debouncedDynamicLoad = async (eventData, figure) => {
    if (dateSliced) {
      const data = { ...figure };
      DynamicLoad({
        event: eventData,
        figure: data,
      }).then(async (toUpdate) => {
        autoScaling(eventData, toUpdate).then((scaled) => {
          if (!scaled.to_update) return;
          setYaxisFixedRange(scaled.yaxis_fixedrange);
          setPlotData({ ...toUpdate, layout: scaled.to_update });
        });
      });
    } else {
      const scaled = await autoScaling(eventData, figure);
      if (!scaled.to_update) return;
      setYaxisFixedRange(scaled.yaxis_fixedrange);
      setPlotData({ ...figure, layout: scaled.to_update });
    }
  };

  const autoscaleButton = useCallback(() => {
    // We need to check if the button is active or not
    const title = "Auto Scale (Ctrl+Shift+A)";
    const button =
      barButtons[title] || document.querySelector(`[data-title="${title}"]`);
    let active = true;

    if (button.style.border === "transparent") {
      plotDiv.removeAllListeners("plotly_relayout");
      active = false;
      plotDiv.on("plotly_relayout", async (eventdata) => {
        if (eventdata["xaxis.range[0]"] === undefined) return;
        const debounceTimer = eventdata["relayout"] ? 0 : 300;
        if (
          !eventdata["relayout"] &&
          isoDateRegex.test(
            eventdata["xaxis.range[0]"].toString().replace(" ", "T"),
          )
        ) {
          const date1 = new Date(eventdata["xaxis.range[0]"].replace(" ", "T"));
          const date2 = new Date(eventdata["xaxis.range[1]"].replace(" ", "T"));

          if (date2.getTime() - date1.getTime() < 3600000 * 2) {
            const d1 = new Date(date1.getTime() - 3600000 * 2);
            const d2 = new Date(date2.getTime() + 3600000 * 2);

            eventdata["xaxis.range[0]"] = formatDate(d1);
            eventdata["xaxis.range[1]"] = formatDate(d2);
            eventdata["relayout"] = true;
            return Plotly.relayout(plotDiv, eventdata);
          }
        }
        debounce(async () => {
          debouncedDynamicLoad(eventdata, originalData);
        }, debounceTimer)();
      });
    }
    // If the button isn't active, we remove the listener so
    // the graphs don't autoscale anymore
    else {
      plotDiv.removeAllListeners("plotly_relayout");
      yaxisFixedRange.forEach((yaxis) => {
        plotDiv.layout[yaxis].fixedrange = false;
      });
      setYaxisFixedRange([]);
      if (dateSliced) {
        plotDiv.on(
          "plotly_relayout",
          debounce(async (eventdata) => {
            if (eventdata["xaxis.range[0]"] === undefined) return;
            debouncedDynamicLoad(eventdata, originalData);
          }, 300),
        );
      }
    }

    button_pressed(title, active);
  }, [
    barButtons,
    dateSliced,
    debouncedDynamicLoad,
    originalData,
    plotDiv,
    yaxisFixedRange,
  ]);

  function changecolorButton() {
    // We need to check if the button is active or not
    const title = "Edit Color (Ctrl+E)";
    const button =
      barButtons[title] || document.querySelector(`[data-title="${title}"]`);
    let active = true;

    if (button.style.border === "transparent") {
      active = false;
    }

    setColorActive(!active);
    button_pressed(title, active);
  }

  useEffect(() => {
    if (autoScale) {
      const scale = !autoScale;
      console.log("activateAutoScale", scale);
      autoscaleButton();
      setAutoScaling(false);
    }
  }, [autoScale]);

  useEffect(() => {
    if (changeColor) {
      changecolorButton();
      setChangeColor(false);
    }
  }, [changeColor]);

  useEffect(() => {
    if (changeTheme) {
      try {
        console.log("changeTheme", changeTheme);
        const TRACES = originalData?.data.filter(
          (trace) => trace?.name?.trim() === "Volume",
        );
        const darkmode = !darkMode;

        window.document.body.style.backgroundColor = darkmode ? "#000" : "#fff";

        originalData.layout.font = {
          ...(originalData.layout.font || {}),
          color: darkmode ? "#fff" : "#000",
        };

        const changeIcon = darkmode ? ICONS.sunIcon : ICONS.moonIcon;

        document
          .querySelector('[data-title="Change Theme"]')
          .getElementsByTagName("path")[0]
          .setAttribute("d", changeIcon.path);

        document
          .querySelector('[data-title="Change Theme"]')
          .getElementsByTagName("svg")[0]
          .setAttribute("viewBox", changeIcon.viewBox);

        const volumeColorsDark = {
          "#009600": "#00ACFF",
          "#c80000": "#e4003a",
        };
        const volumeColorsLight = {
          "#e4003a": "#c80000",
          "#00ACFF": "#009600",
        };

        const volumeColors = darkmode ? volumeColorsDark : volumeColorsLight;

        TRACES.forEach((trace) => {
          if (trace.type === "bar" && Array.isArray(trace.marker.color))
            trace.marker.color = trace.marker.color.map((color) => {
              return volumeColors[color] || color;
            });
        });
        originalData.layout.template = darkmode
          ? DARK_CHARTS_TEMPLATE
          : LIGHT_CHARTS_TEMPLATE;
        setPlotData({ ...originalData });
        setDarkMode(darkmode);
        setChangeTheme(false);
      } catch (e) {
        console.log("error", e);
      }
    }
  }, [changeTheme]);

  useEffect(() => {
    if (plotLoaded) {
      setDarkMode(true);
      setAutoScaling(false);
      const captureButtons = [
        "Download CSV",
        "Download Chart as Image",
        "Overlay chart from CSV",
        "Add Text",
        "Change Titles",
        "Auto Scale (Ctrl+Shift+A)",
        "Reset Axes",
      ];
      const autoscale = document.querySelector('[data-title="Autoscale"]');
      if (autoscale) {
        autoscale
          .getElementsByTagName("path")[0]
          .setAttribute("d", PlotlyIcons.home.path);
        autoscale.setAttribute("data-title", "Reset Axes");
      }

      window.MODEBAR = document.getElementsByClassName(
        "modebar-container",
      )[0] as HTMLElement;
      const modeBarButtons = window.MODEBAR.getElementsByClassName(
        "modebar-btn",
      ) as HTMLCollectionOf<HTMLElement>;

      window.MODEBAR.style.cssText = `${window.MODEBAR.style.cssText}; display:flex;`;

      if (modeBarButtons) {
        const barbuttons: any = {};
        for (let i = 0; i < modeBarButtons.length; i++) {
          const btn = modeBarButtons[i];
          if (captureButtons.includes(btn.getAttribute("data-title"))) {
            btn.classList.add("ph-capture");
          }
          btn.style.border = "transparent";
          barbuttons[btn.getAttribute("data-title")] = btn;
        }
        setModeBarButtons(barbuttons);
      }

      if (plotData?.layout?.yaxis?.type !== undefined) {
        if (plotData.layout.yaxis.type === "log" && !LogYaxis) {
          console.log("yaxis.type changed to log");
          setLogYaxis(true);

          // const layout_update = {
          //   "yaxis.exponentformat": "none"
          // };
          // Plotly.update(plotDiv, {}, layout_update);
        }
        if (plotData.layout.yaxis.type === "linear" && LogYaxis) {
          console.log("yaxis.type changed to linear");
          setLogYaxis(false);

          // We update the yaxis exponent format to none,
          // set the tickformat to null and the exponentbase to 10
          const layout_update = {
            "yaxis.exponentformat": "none",
            "yaxis.tickformat": null,
            "yaxis.exponentbase": 10,
          };
          Plotly.update(plotDiv, {}, layout_update);
        }
      }

      // We check to see if window.export_image is defined
      if (window.export_image !== undefined) {
        // We get the extension of the file and check if it is valid
        const filename = window.export_image.split("/").pop();
        const extension = filename.split(".").pop().replace("jpg", "jpeg");

        if (["jpeg", "png", "svg", "pdf"].includes(extension))
          return non_blocking(async function () {
            await hideModebar();
            await saveImage("MainChart", filename.split(".")[0], extension);
          }, 2)();
      }

      window.addEventListener("resize", async function () {
        const update = await ResizeHandler({
          plotData,
          volumeBars,
          setMaximizePlot,
        });
        const layout_update = update.layout_update;
        const newPlotData = update.plotData;
        const volume_update = update.volume_update;

        if (Object.keys(layout_update).length > 0) {
          setPlotData(newPlotData);
          setVolumeBars(volume_update);
          Plotly.update(plotDiv, {}, layout_update);
        }
      });

      if (theme !== "dark") {
        setChangeTheme(true);
      }

      const traceTypes = originalData.data.map(
        (trace) => trace.type === "candlestick",
      );
      if (
        (originalData.data[0]?.x !== undefined &&
          originalData.data[0]?.x.length <= 2000) ||
        !traceTypes.includes(true)
      )
        return;
      setModal({
        name: "alertDialog",
        data: {
          title: "Warning",
          content: `Data has been truncated to 2000 points for performance reasons.
						Please use the zoom tool to see more data.`,
        },
      });
      const new_figure = CreateDataXrange(originalData);
      setPlotData(new_figure);
      setDateSliced(true);
      setAutoScaling(true);
    }
  }, [plotLoaded]);

  const plotComponent = useMemo(
    () => (
      <PlotComponent
        onInitialized={(_figure, graphDiv) => {
          if (!plotDiv) {
            if (graphDiv) {
              graphDiv.globals = globals;
              setPlotDiv(graphDiv);
            }
          }
          if (!plotLoaded) setPlotLoaded(true);
        }}
        className="w-full h-full"
        divId="plotlyChart"
        data={plotData.data}
        layout={plotData.layout}
        config={PlotConfig({
          setModal: setModal,
          changeTheme: setChangeTheme,
          autoScaling: setAutoScaling,
          Loading: setLoading,
          changeColor: setChangeColor,
          downloadFinished: setDownloadFinished,
        })}
      />
    ),
    [
      plotDiv,
      originalData,
      plotLoaded,
      plotData,
      globals,
      setPlotDiv,
      setPlotLoaded,
      setModal,
      setChangeTheme,
      setAutoScaling,
      setLoading,
      onChangeColor,
      setDownloadFinished,
    ],
  );

  const memoizedAlertDialog = useMemo(() => {
    return (
      <AlertDialog
        title={modal?.data?.title}
        content={modal?.data?.content}
        open={modal?.name === "alertDialog"}
        close={onClose}
      />
    );
  }, [modal, onClose]);

  const memoizedOverlayChartDialog = useMemo(() => {
    return (
      <OverlayChartDialog
        addOverlay={(overlay) => {
          console.log(overlay);
          overlay.layout.showlegend = true;
          setOriginalData(overlay);
          setPlotData(overlay);
        }}
        plotlyData={originalData}
        setLoading={setLoading}
        open={modal?.name === "overlayChart"}
        close={onClose}
      />
    );
  }, [modal, plotData, onClose, setPlotData, setLoading]);

  const memoizedTitleChartDialog = useMemo(() => {
    return (
      <TitleChartDialog
        updateTitle={(title) => setChartTitle(title)}
        updateAxesTitles={(axesTitles) => setAxesTitles(axesTitles)}
        defaultTitle={chartTitle}
        plotlyData={plotData}
        open={modal?.name === "titleDialog"}
        close={onClose}
      />
    );
  }, [modal, plotData, chartTitle, onClose]);

  const memoizedTextChartDialog = useMemo(() => {
    return (
      <TextChartDialog
        popupData={modal?.name === "textDialog" ? modal?.data : null}
        open={modal?.name === "textDialog"}
        close={onClose}
        addAnnotation={(data) => onAddAnnotation(data)}
        deleteAnnotation={(data) => onDeleteAnnotation(data)}
      />
    );
  }, [
    modal,
    onAddAnnotation,
    onDeleteAnnotation,
    onClose,
    plotData,
    setPlotData,
  ]);

  const memoizedChangeColor = useMemo(() => {
    return <ChangeColor open={colorActive} onColorChange={onChangeColor} />;
  }, [colorActive, onChangeColor]);

  const memoizedDownloadFinishedDialog = useMemo(() => {
    return (
      <DownloadFinishedDialog
        open={modal?.name === "downloadFinished"}
        close={onClose}
      />
    );
  }, [modal, onClose]);

  const memoizedChartHotkeys = useMemo(() => {
    return (
      <ChartHotkeys
        setModal={setModal}
        Loading={setLoading}
        changeColor={setChangeColor}
        downloadFinished={setDownloadFinished}
      />
    );
  }, [setModal, setLoading, setChangeColor, setDownloadFinished]);

  return (
    <div className="relative h-full">
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center z-[100]">
          <svg
            className="animate-spin h-20 w-20 text-white"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8v8z"
            />
          </svg>
        </div>
      )}
      <div id="loading" className="saving">
        <div id="loading_text" className="loading_text" />
        <div id="loader" className="loader" />
      </div>
      {memoizedAlertDialog}
      {memoizedOverlayChartDialog}
      {memoizedTitleChartDialog}
      {memoizedTextChartDialog}
      {memoizedChangeColor}
      {memoizedDownloadFinishedDialog}
      {memoizedChartHotkeys}

      <div className="relative h-full" id="MainChart">
        <div className="_header relative gap-4 py-2 text-center text-xs flex items-center justify-between px-4 text-white">
          <div className="w-1/3">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="64"
              height="40"
              fill="none"
              viewBox="0 0 64 40"
            >
              <path
                fill="#fff"
                d="M61.283 3.965H33.608v27.757h25.699V19.826H37.561v-3.965H63.26V3.965h-1.977zM39.538 23.792h15.815v3.965H37.561v-3.965h1.977zM59.306 9.913v1.983H37.561V7.931h21.745v1.982zM33.606 0h-3.954v3.965H33.606V0zM25.7 3.966H0V15.86h25.7v3.965H3.953v11.896h25.7V3.966h-3.955zm0 21.808v1.983H7.907v-3.965h17.791v1.982zm0-15.86v1.982H3.953V7.931h21.745v1.982zM37.039 35.693v2.952l-.246-.246-.245-.245-.245-.247-.245-.246-.246-.246-.245-.245-.245-.247-.247-.246-.245-.246-.245-.246-.245-.246-.246-.246h-.49v3.936h.49v-3.198l.246.246.245.246.245.246.245.246.246.246.246.246.245.247.246.245.245.246.245.247.245.246.246.245.245.246h.245v-3.936h-.49zM44.938 37.17h-.491v-1.477h-2.944v3.937h3.93v-2.46h-.495zm-2.944-.246v-.739h1.962v.984h-1.962v-.245zm2.944.984v1.23h-2.944V37.66h2.944v.247zM52.835 37.17h-.49v-1.477h-2.946v3.937h3.925v-2.46h-.489zm-2.944-.246v-.739h1.963v.984h-1.965l.002-.245zm2.944.984v1.23H49.89V37.66h2.946v.247zM29.174 35.693H25.739v3.936H29.663v-.491H26.229v-.984h2.943v-.493H26.229v-1.476h3.434v-.492h-.489zM13.37 35.693H9.934v3.937h3.925v-3.937h-.49zm0 .738v2.709h-2.945v-2.955h2.943l.001.246zM21.276 35.693h-3.435v3.937h.491v-1.476h3.434v-2.461h-.49zm0 .738v1.23h-2.944v-1.476h2.944v.246z"
              />
            </svg>
          </div>
          <p className="font-bold w-1/3 flex flex-col gap-0.5 items-center">
            {chartTitle}
            {/* {source && (
						<span className="font-normal text-[10px]">{`[${source}]`}</span>
					)} */}
          </p>
          <p className="w-1/3 text-right text-xs">
            {new Intl.DateTimeFormat("en-GB", {
              dateStyle: "full",
              timeStyle: "long",
            })
              .format(date)
              .replace(/:\d\d /, " ")}
            <br />
            <span className="text-grey-400">{cmd}</span>
          </p>
          {/* {source && typeof source === "string" && source.includes("*") && (
					<p className="text-[8px] absolute bottom-0 right-4">
						*not affiliated
					</p>
				)} */}
        </div>
        <div
          className={clsx("w-full sm:pb-12", {
            "h-[calc(100%-10px)]": maximizePlot,
            "h-[calc(100%-50px)]": !maximizePlot,
          })}
        >
          {plotComponent}
        </div>
      </div>
    </div>
  );
}

export default React.memo(Chart);
