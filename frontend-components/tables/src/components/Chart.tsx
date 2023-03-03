//@ts-ignore
import Plot from "react-plotly.js";

const COLORS = [
  "rgb(31,119,180)",
  "rgb(255,127,14)",
  "rgb(44,160,44)",
  "rgb(214,39,40)",
  "rgb(148,103,189)",
  "rgb(140,86,75)",
  "rgb(227,119,194)",
  "rgb(127,127,127)",
];

export default function Chart({ values }: { values: number[][] }) {
  if (!values) return null;
  const data = values.map((value, idx) => ({
    x: value.map((_, i) => i),
    y: value,
    type: "bar",
    marker: {
      color: COLORS[idx],
      opacity: 0.6,
      line: {
        color: COLORS[idx],
        width: 1.5,
      },
    },
  }));
  console.log(data);
  return (
    <Plot
      data={data}
      layout={{
        plot_bgcolor: "rgba(0,0,0,1)",
        paper_bgcolor: "rgba(0,0,0,1)",
      }}
      config={{
        displaylogo: false,
        responsive: true,
      }}
    />
  );
}
