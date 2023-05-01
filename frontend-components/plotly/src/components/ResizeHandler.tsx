//@ts-nocheck
import { Figure } from "react-plotly.js";
import { hideModebar } from "./PlotlyConfig";

export default async function ResizeHandler({
  plotData,
  Volume,
}: {
  plotData: Figure;
  Volume: any;
}) {
  // We hide the modebar and set the number of ticks to 5
  const XAXIS = Object.keys(plotData.layout)
    .filter((x) => x.startsWith("xaxis"))
    .filter((x) => plotData.layout[x].showticklabels);

  const TRACES = plotData.data.filter((trace) =>
    trace?.name?.startsWith("Volume")
  );

  let layout_update: any = {};
  let volume: any = Volume || { old_nticks: {} };

  const width = window.innerWidth;
  const height = window.innerHeight;
  let tick_size =
    height > 420 && width < 920 ? 9 : height > 420 && width < 500 ? 10 : 8;

  if (width < 750) {
    // We hide the modebar and set the number of ticks to 5

    TRACES.forEach((trace) => {
      if (trace.type == "bar") {
        trace.opacity = 1;
        trace.marker.line.width = 0.09;
        if (Volume.yaxis == undefined) {
          volume.yaxis = "yaxis" + trace.yaxis.replace("y", "");
          layout_update[volume.yaxis + ".tickfont.size"] = tick_size;
          volume.tickfont = plotData.layout[volume.yaxis].tickfont || {};

          plotData.layout.margin.l -= 40;
        }
      }
    });
    XAXIS.forEach((x) => {
      if (volume.old_nticks?.[x] == undefined) {
        layout_update[x + ".nticks"] = 6;
        volume.old_nticks[x] = plotData.layout[x].nticks || 10;
      }
    });
    await hideModebar();
  } else if (window.MODEBAR.style.cssText.includes("display: none")) {
    // We show the modebar
    await hideModebar(false);

    if (Volume.old_nticks != undefined) {
      XAXIS.forEach((x) => {
        if (volume.old_nticks[x] != undefined) {
          layout_update[x + ".nticks"] = volume.old_nticks[x];
          volume.old_nticks[x] = undefined;
        }
      });
    }

    if (Volume.yaxis != undefined) {
      TRACES.forEach((trace) => {
        if (trace.type == "bar") {
          trace.opacity = 0.5;
          trace.marker.line.width = 0.2;
          layout_update[volume.yaxis + ".tickfont.size"] =
            volume.tickfont.size + 3;
          plotData.layout.margin.l += 40;
          volume.yaxis = undefined;
        }
      });
    }
  }

  return {
    volume_update: volume,
    layout_update: layout_update,
    plotData: plotData,
  };
}
