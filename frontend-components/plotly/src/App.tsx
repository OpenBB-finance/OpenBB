//@ts-nocheck
import { PostHogProvider } from "posthog-js/react";
import { useEffect, useState } from "react";
import Chart from "./components/Chart";
import { candlestickMockup } from "./data/mockup";

declare global {
  [Exposed === Window, SecureContext];
  interface Window {
    json_data: any;
    export_image: string;
    save_image: boolean;
    title: string;
    Plotly: any;
    MODEBAR: HTMLElement;
    download_path: string;
    pywry: any;
  }
}

function App() {
  const [json_data, setData] = useState(
    process.env.NODE_ENV === "production" ? null : candlestickMockup,
  );
  const [options, setOptions] = useState({});

  useEffect(() => {
    if (process.env.NODE_ENV === "production") {
      const interval = setInterval(() => {
        if (window.json_data) {
          const plotly_json = window.json_data;
          console.log(plotly_json);
          setData(plotly_json);
          clearInterval(interval);
        }
      }, 100);
      return () => clearInterval(interval);
    }
  }, []);

  const transformData = (data: any) => {
    if (!data) return null;
    const globals = {
      added_traces: [],
      csv_yaxis_id: null,
      cmd_src_idx: null,
      cmd_idx: null,
      cmd_src: "",
      old_margin: null,
      title: "",
    };
    const filename = data.layout?.title?.text
      .replace(/ -/g, "")
      .replace(/-/g, "")
      .replace(/<b>|<\/b>/g, "")
      .replace(/ /g, "_");
    const date = new Date().toISOString().slice(0, 10).replace(/-/g, "");
    const time = new Date().toISOString().slice(11, 19).replace(/:/g, "");
    window.title = `openbb_${filename}_${date}_${time}`.replace(/_{2,}/g, "_");

    if (data.layout.annotations !== undefined) {
      data.layout.annotations.forEach(function (annotation) {
        if (annotation.text !== undefined)
          if (annotation.text[0] === "/") {
            globals.cmd_src = annotation.text;
            globals.cmd_idx = data.layout.annotations.indexOf(annotation);
            annotation.text = "";

            const margin = data.layout.margin;
            globals.old_margin = { ...margin };
            if (margin.t !== undefined && margin.t > 40) margin.t = 40;

            if (data.cmd === "/stocks/candle") margin.r -= 50;
          }
      });
    }

    // We add spaces to all trace names, due to Fira Code font width issues
    // to make sure that the legend is not cut off
    data.data.forEach(function (trace) {
      if (trace.name !== undefined) {
        trace.hoverlabel = {
          namelength: -1,
        };
      }
    });

    const title = data.layout?.title?.text || "Interactive Chart";
    globals.title = title;
    return {
      data: data,
      date: new Date(),
      globals: globals,
      cmd: data.command_location,
      posthog: data.posthog,
      python_version: data.python_version,
      pywry_version: data.pywry_version,
      terminal_version: data.terminal_version,
      theme: data.theme,
      title,
    };
  };

  const transformedData = transformData(json_data);

  if (transformedData) {
    if (transformedData.posthog.collect_logs && !options) {
      const opts = {
        api_host: "https://app.posthog.com",
        autocapture: {
          css_selector_allowlist: [".ph-capture"],
        },
        capture_pageview: false,
        loaded: function (posthog: any) {
          const log_id = transformedData?.log_id || "";

          if (log_id !== "" && log_id !== "REPLACE_ME")
            posthog.identify(log_id);

          posthog.onFeatureFlags(function () {
            if (
              !posthog.isFeatureEnabled("record-pywry", { send_event: false })
            )
              posthog.stopSessionRecording();

            if (
              !posthog.isFeatureEnabled("collect-logs-pywry", {
                send_event: false,
              })
            )
              posthog.opt_out_capturing();
            else if (posthog.has_opted_out_capturing())
              posthog.opt_in_capturing();
          });
        },
      };
      setOptions(opts);
    }

    const info = {
      INFO: {
        command: transformedData.cmd,
        title: transformedData.title,
        date: transformedData.date,
        python_version: transformedData.python_version,
        pywry_version: transformedData.pywry_version,
        terminal_version: transformedData.terminal_version,
      },
    };

    const chartDiv = (
      <Chart
        json={transformedData.data}
        date={transformedData.date}
        cmd={transformedData.cmd}
        title={transformedData.title}
        globals={transformedData.globals}
        theme={transformedData.theme}
        info={info}
      />
    );

    if (transformedData.posthog.collect_logs && options) {
      return (
        <PostHogProvider
          apiKey="phc_vhssDAMod5qIplznQ75Kdgz4aB1qPFmeVmfEOZ4hkRw"
          options={options}
        >
          {chartDiv}
        </PostHogProvider>
      );
    }

    return chartDiv;
  } else
    return (
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
    );
}

export default App;
