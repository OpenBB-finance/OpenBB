import { Icons as PlotlyIcons } from "plotly.js-dist-min";
import { downloadCSV, downloadImage } from "../utils/utils";
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
            hideModebar(true);
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


export function ChartHotkeys({
  setModal,
  Loading,
  changeColor,
  downloadFinished,
}: {
  setModal: (modal: { name: string; data?: any }) => void;
  Loading: (change: boolean) => void;
  changeColor: (change: boolean) => void;
  downloadFinished: (change: boolean) => void;
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
  );
  useHotkeys(
    "ctrl+e",
    () => {
      changeColor(true);
    },
    { preventDefault: true },
  );
  useHotkeys(
    "ctrl+shift+s",
    async () => {
      setModal({ name: "downloadCsv" });
      await downloadCSV(
        document.getElementById("plotlyChart") as any,
        downloadFinished,
      );
    },
    { preventDefault: true },
  );
  useHotkeys(
    "ctrl+s",
    async () => {
      hideModebar();
      downloadImage("MainChart", hideModebar, Loading, downloadFinished);
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
