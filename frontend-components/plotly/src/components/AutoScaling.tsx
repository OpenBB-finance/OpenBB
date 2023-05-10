//@ts-nocheck
import { Figure } from "react-plotly.js";

export default async function autoScaling(
  eventdata: Readonly<Plotly.PlotRelayoutEvent>,
  graphs: Figure
) {
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

      return to_update;
    }
  } catch (e) {
    console.log(`Error in AutoScaling: ${e}`);
  }
  return {};
}
