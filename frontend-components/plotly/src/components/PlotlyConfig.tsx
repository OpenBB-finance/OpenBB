import { Icons as PlotlyIcons } from "plotly.js-dist-min";
import { downloadCSV, downloadImage } from "../utils/utils";
import { ICONS } from "./Config";

export function hideModebar(hide = true) {
  return new Promise((resolve) => {
    if (!window.MODEBAR) {
      window.MODEBAR = window.document.getElementsByClassName(
        "modebar-container",
      )[0] as HTMLElement;
      window.MODEBAR.style.cssText = `${window.MODEBAR.style.cssText}; display:flex;`;
    }
    let includes_text = "display: none";
    if (window.MODEBAR) {
      if (window.MODEBAR.style.cssText.includes("display: none") || !hide) {
        includes_text = "display: flex";
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
  downloadFinished,
}: {
  setModal: (modal: { name: string; data?: any }) => void;
  changeTheme: (change: boolean) => void;
  autoScaling: (change: boolean) => void;
  Loading: (change: boolean) => void;
  changeColor: (change: boolean) => void;
  downloadFinished: (change: boolean) => void;
}) {
  const CONFIG = {
    plotGlPixelRatio: 1,
    scrollZoom: true,
    responsive: true,
    displaylogo: false,
    displayModeBar: true,
    modeBarButtonsToRemove: ["lasso2d", "select2d", "downloadImage"],
    modeBarButtons: [
      [
        {
          name: "Download CSV (Ctrl+Shift+S)",
          icon: ICONS.downloadCsv,
          click: async function (gd: any) {
            await downloadCSV(gd, downloadFinished);
          },
        },
        {
          name: "Download Chart as Image (Ctrl+S)",
          icon: ICONS.downloadImage,
          click: async function () {
            hideModebar();
            await downloadImage(
              "MainChart",
              hideModebar,
              Loading,
              downloadFinished,
            );
          },
        },
        // {
        //   name: "Upload Image (Ctrl+U)",
        //   icon: Plotly.Icons.uploadImage,
        //   click: function (gd) {
        //     downloadImage();
        //   },
        // },
      ],
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
