import { useEffect, useRef } from "react";
import type { EChartsOption } from "echarts";

interface MacroStudyChartProps {
  option: EChartsOption;
  height?: number;
  title?: string;
}

export function MacroStudyChart({ option, height = 320, title }: MacroStudyChartProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<{ dispose: () => void } | null>(null);

  useEffect(() => {
    let active = true;
    let handleResize: (() => void) | null = null;

    const loadChart = async () => {
      if (!containerRef.current) {
        return;
      }

      const { macroEcharts } = await import("../../lib/echartsMacro");
      if (!active || !containerRef.current) {
        return;
      }

      const chart =
        macroEcharts.getInstanceByDom(containerRef.current) ??
        macroEcharts.init(containerRef.current, undefined, {
          renderer: "canvas",
        });

      chartRef.current = chart;
      chart.setOption(option, true);
      handleResize = () => chart.resize();
      window.addEventListener("resize", handleResize);
    };

    void loadChart();

    return () => {
      active = false;
      if (handleResize) {
        window.removeEventListener("resize", handleResize);
      }
      chartRef.current?.dispose();
      chartRef.current = null;
    };
  }, [option]);

  return (
    <div>
      {title ? (
        <div className="mb-2 flex items-center justify-between">
          <h3 className="body-sm-medium text-theme-primary">{title}</h3>
        </div>
      ) : null}
      <div ref={containerRef} style={{ width: "100%", height }} />
    </div>
  );
}
