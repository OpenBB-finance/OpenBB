//@ts-nocheck
import { Figure } from "react-plotly.js";
import { hideModebar } from "./PlotlyConfig";

export default async function ResizeHandler({
  plotData,
  volumeBars,
  setMaximizePlot,
}: {
  plotData: Figure;
  volumeBars: any;
  setMaximizePlot: (value: boolean) => void;
}) {
  // We hide the modebar and set the number of ticks to 5
  const XAXIS = Object.keys(plotData.layout)
    .filter((x) => x.startsWith("xaxis"))
    .filter(
      (x) =>
        plotData.layout[x].showticklabels ||
        plotData.layout[x].matches === undefined,
    );

  const TRACES = plotData.data.filter(
    (trace) => trace?.name?.trim() === "Volume",
  );

  const layout_update: any = {};
  const volume: any = volumeBars || { old_nticks: {} };

  const width = window.innerWidth;
  const height = window.innerHeight;
  const tick_size =
    height > 420 && width < 920 ? 8 : height > 420 && width < 500 ? 9 : 7;

  if (width < 850) {
    // We hide the modebar and set the number of ticks to 6

    TRACES.forEach((trace) => {
      if (trace.type === "bar") {
        trace.opacity = 1;
        trace.marker.line.width = 0.09;
        if (volumeBars.yaxis === undefined) {
          volume.yaxis = `yaxis${trace.yaxis.replace("y", "")}`;
          layout_update[`${volume.yaxis}.tickfont.size`] = tick_size;
          volume.tickfont = plotData.layout[volume.yaxis].tickfont || {};

          plotData.layout.margin.l -= 40;
        }
      }
    });

    XAXIS.forEach((x) => {
      if (volumeBars.old_nticks?.[x] === undefined) {
        layout_update[`${x}.nticks`] = 6;
        volume.old_nticks[x] = plotData.layout[x].nticks || 10;
      }
    });
    setMaximizePlot(true);

    await hideModebar(true);
  } else if (
    width > 850 &&
    window.MODEBAR.style.cssText.includes("display: none")
  ) {
    // We show the modebar
    await hideModebar(false);
    setMaximizePlot(false);

    if (volumeBars.old_nticks !== undefined) {
      XAXIS.forEach((x) => {
        if (volumeBars.old_nticks[x] !== undefined) {
          layout_update[`${x}.nticks`] = volume.old_nticks[x];
          volume.old_nticks[x] = undefined;
        }
      });
    }

    if (volumeBars.yaxis !== undefined) {
      TRACES.forEach((trace) => {
        if (trace.type === "bar") {
          trace.opacity = 0.5;
          trace.marker.line.width = 0.2;
          layout_update[`${volume.yaxis}.tickfont.size`] =
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
