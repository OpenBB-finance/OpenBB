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

const plot_layout = {
  height: window.innerHeight * 0.7,
  width: window.innerWidth * 0.8,
  font: {
    color: "#F5EFF3",
    size: 16,
  },
  annotationdefaults: {
    showarrow: false,
  },
  autotypenumbers: "strict",
  colorway: [
    "#ffed00",
    "#ef7d00",
    "#e4003a",
    "#c13246",
    "#822661",
    "#48277c",
    "#005ca9",
    "#00aaff",
    "#9b30d9",
    "#af005f",
    "#5f00af",
    "#af87ff",
  ],
  xaxis: {
    automargin: true,
    autorange: true,
    rangeslider: {
      visible: false,
    },
    showgrid: true,
    showline: true,
    tickfont: {
      size: 14,
    },
    zeroline: false,
    tick0: 1,
    title: {
      standoff: 20,
    },
    linecolor: "#F5EFF3",
    mirror: true,
    ticks: "outside",
  },
  yaxis: {
    anchor: "x",
    automargin: true,
    fixedrange: false,
    zeroline: false,
    showgrid: true,
    showline: true,
    side: "right",
    tick0: 0.5,
    title: {
      standoff: 20,
    },
    gridcolor: "#283442",
    linecolor: "#F5EFF3",
    mirror: true,
    ticks: "outside",
  },
  plot_bgcolor: "rgba(0,0,0,1)",
  paper_bgcolor: "rgba(0,0,0,1)",
  dragmode: "pan",
};


export default function Chart({ values }: { values: number[][] }) {
  if (!values) return null;
  console.log(values);
  const data = values.map((value, idx) => ({
    x: value.map((_, i) => i),
    y: value,
    type: "bar",
    showlegend: false,
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
      layout={plot_layout}
      config={{
        displaylogo: false,
        responsive: true,
        scrollZoom: true,
      }}
    />
  );
}
