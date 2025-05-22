import { Icons as PlotlyIcons } from "plotly.js-dist-min";
import * as Plotly from "plotly.js-dist-min";
import { useHotkeys } from "react-hotkeys-hook";
import { ICONS } from "./Config";


export function hideModebar(hide?: boolean) {
  return new Promise((resolve) => {
    if (!window.MODEBAR) {
      window.MODEBAR = window.document.getElementsByClassName(
        "modebar-container",
      )[0] as HTMLElement;
      window.MODEBAR.style.cssText = `${window.MODEBAR.style.cssText}; display:flex;`;
    }

    if (window.MODEBAR) {
      if (hide) {
        window.MODEBAR.style.cssText = `${window.MODEBAR.style.cssText}; display:none;`;
      } else if (window.MODEBAR.style.cssText.includes("none")) {
        window.MODEBAR.style.cssText = `${window.MODEBAR.style.cssText}; display:flex;`;
      } else {
        window.MODEBAR.style.cssText = `${window.MODEBAR.style.cssText}; display:none;`;
      }
      resolve(true);
    }
  });
}

export function PlotConfig({
  setModal,
  changeTheme,
  autoScaling,
  Loading,
  changeColor,
}: {
  setModal: (modal: { name: string; data?: any }) => void;
  changeTheme: (change: boolean) => void;
  autoScaling: (change: boolean) => void;
  Loading: (change: boolean) => void;
  changeColor: (change: boolean) => void;
}) {
  const CONFIG = {
    plotGlPixelRatio: 1,
    scrollZoom: true,
    responsive: true,
    displaylogo: false,
    displayModeBar: "hover",
    edits: {
      legendPosition: true,
      legendText: true,
      colorbarPosition: true,
      annotationPosition: true,
      annotationTail: true,
      annotationText: true,
    },
    showTips: false,
    setBackground: "transparent",
    modeBarButtonsToRemove: ["lasso2d", "select2d", "saveImage"],
    modeBarButtons: [
      [
        {
          name: "Edit Color (Ctrl+E)",
          icon: ICONS.changeColor,
          click: function () {
            changeColor(true);
          },
        },
        "drawline",
        "drawopenpath",
        "drawcircle",
        "drawrect",
        "eraseshape",
      ],
      [
        {
          name: "Overlay chart from CSV (Ctrl+O)",
          icon: ICONS.plotCsv,
          click: function () {
            setModal({ name: "overlayChart" });
          },
        },
        {
          name: "Add Text (Ctrl+T)",
          icon: ICONS.addText,
          click: function () {
            setModal({ name: "textDialog", data: { text: "" } });
          },
        },
        {
          name: "Change Titles (Ctrl+Shift+T)",
          icon: ICONS.changeTitle,
          click: function () {
            setModal({ name: "titleDialog" });
          },
        },
        {
          name: "Change Theme",
          icon: ICONS.sunIcon,
          click: function () {
            changeTheme(true);
          },
        },
      ],
      ["hoverClosestCartesian", "hoverCompareCartesian", "toggleSpikelines"],
      [
        {
          name: "Auto Scale (Ctrl+Shift+A)",
          icon: PlotlyIcons.autoscale,
          click: function () {
            autoScaling(true);
          },
        },
        "zoomIn2d",
        "zoomOut2d",
        "autoScale2d",
        "zoom2d",
        "pan2d",
      ],
    ],
  };
  return CONFIG;
}


export function ChartHotkeys({
  setModal,
  Loading,
  changeColor,
}: {
  setModal: (modal: { name: string; data?: any }) => void;
  Loading: (change: boolean) => void;
  changeColor: (change: boolean) => void;
}) {
  useHotkeys(
    "ctrl+shift+t",
    () => {
      setModal({ name: "titleDialog" });
    },
    { preventDefault: true },
  );
  useHotkeys(
    "ctrl+t",
    () => {
      setModal({ name: "textDialog" });
    },
    { preventDefault: true },
  );
  useHotkeys(
    "ctrl+o",
    () => {
      setModal({ name: "overlayChart" });
    },
    { preventDefault: true },
  );
  useHotkeys(
    ["ctrl+shift+h", "ctrl+h"],
    () => {
      hideModebar();
    },
    { preventDefault: true },
  );  useHotkeys(
    "ctrl+l",
    () => {
      // Toggle log scale when Ctrl+L is pressed
      const plotDiv = document.getElementById("plotlyChart") as any;
      if (plotDiv && plotDiv._fullLayout) {
        // Check if this is an OHLC/Candle chart or a time series Scatter
        const isOHLCOrCandle = plotDiv._fullData.some((trace: any) =>
          trace.type === 'ohlc' || trace.type === 'candlestick'
        );

        const isTimeSeriesScatter = plotDiv._fullData.some((trace: any) =>
          trace.type === 'scatter' && (trace.mode === 'lines' || trace.mode === 'lines+markers') &&
          trace.x && trace.x.length > 0 && (typeof trace.x[0] === 'string' || trace.x[0] instanceof Date)
        );

        if (isOHLCOrCandle || isTimeSeriesScatter) {
          // Only toggle the main y-axis (yaxis or y1)
          const currentType = plotDiv._fullLayout.yaxis?.type || 'linear';
          const newType = currentType === 'linear' ? 'log' : 'linear';

          // Only modify the main y-axis, leaving all others unchanged
          const updateObj: any = {
            'yaxis.type': newType
          };

          // Apply change ONLY to main y-axis
          console.log("Changing main y-axis scale to:", newType);
          Plotly.relayout(plotDiv, updateObj as any);
        } else {
          console.log("Log scale toggle is only available for OHLC/Candle charts or time series Scatter plots");
        }
      }
    },
    { preventDefault: true },
  );
  useHotkeys(
    "ctrl+e",
    () => {
      changeColor(true);
    },
    { preventDefault: true },
  );

  // Removed the ctrl+shift+s export shortcut

  useHotkeys(
    "ctrl+s",
    () => {
      // Download feature removed
    },
    { preventDefault: true },
  );

  useHotkeys(
    "ctrl+w",
    () => {
      window.close();
    },
    { preventDefault: true },
  );
}
