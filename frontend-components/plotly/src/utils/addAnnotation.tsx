//@ts-nocheck
import {
  Annotations,
  PlotMouseEvent,
  PlotlyHTMLElement,
} from "plotly.js-dist-min";
import { Figure } from "react-plotly.js";

type PopupData = {
  x: number;
  y: number;
  yref: string;
  text: string;
  yshift: number;
  yanchor: string;
  bordercolor: string;
  color: string;
  size: number;
  annotation?: any;
};

export function add_annotation({
  plotData,
  popup_data,
  current_text,
}: {
  plotData: Figure;
  popup_data: PopupData;
  current_text?: string;
}) {
  let x = popup_data.x;
  let y = popup_data.y;
  let yref = popup_data.yref;
  let annotations = plotData?.layout?.annotations || [];
  let index = -1;

  for (let i = 0; i < annotations.length; i++) {
    if (
      annotations[i].x == x &&
      annotations[i].y == y &&
      annotations[i].text == current_text
    ) {
      index = i;
      break;
    }
  }
  if (index == -1) {
    let annotation: Annotations = {
      x: x,
      y: y,
      xref: "x",
      yref: yref,
      xanchor: "center",
      text: popup_data.text,
      showarrow: true,
      arrowhead: 2,
      arrowsize: 1,
      arrowwidth: 2,
      ax: x,
      ay: y + popup_data.yshift,
      ayref: yref,
      axref: "x",
      bordercolor: popup_data.bordercolor,
      bgcolor: "#000000",
      borderwidth: 2,
      borderpad: 4,
      opacity: 0.8,
      font: {
        color: popup_data.color,
        size: popup_data.size,
      },
      clicktoshow: "onoff",
      captureevents: true,
    };
    annotations.push(annotation);
  } else {
    annotations[index].text = popup_data.text;
    annotations[index].font.color = popup_data.color;
    annotations[index].font.size = popup_data.size;
    annotations[index].ay = y + popup_data.yshift;
    annotations[index].bordercolor = popup_data.bordercolor;
  }
  return { annotations: annotations, annotation: annotations[index] };
}

export function plot_text({
  plotData,
  popup_data,
  current_text,
}: {
  plotData: Figure;
  popup_data: PopupData;
  current_text?: string;
}) {
  // Plots text on the chart based on the popup_data
  // If current_text is not null, it will be replaced with the new text
  // If current_text is null, a new annotation will be added
  // popup_data is the data from the popup
  // data is the data from the chart

  console.log("plot_text: current_text", current_text);
  let output = undefined;
  let yaxis = popup_data.yref.replace("y", "yaxis");
  let yrange = plotData.layout[yaxis].range;
  let yshift = (yrange[1] - yrange[0]) * 0.2;

  if (popup_data.yanchor == "below") {
    yshift = -yshift;
  }
  popup_data.yshift = yshift;

  output = add_annotation({ plotData, popup_data, current_text });

  let to_update = { annotations: output.annotations, dragmode: "pan" };
  to_update[yaxis + ".type"] = "linear";
  return { update: to_update, annotation: output.annotation };
}

export function init_annotation({
  plotData,
  popupData,
  setPlotData,
  setModal,
  setOnAnnotationClick,
  setAnnotations,
  onAnnotationClick,
  annotations,
  plotDiv,
}: {
  plotData: Figure;
  popupData: Partial<PopupData>;
  setPlotData: (plotData: Partial<Figure>) => void;
  setModal: (modal: { name: string; data?: any }) => void;
  onAnnotationClick: any;
  setOnAnnotationClick: (onAnnotationClick: any) => void;
  setAnnotations: (annotations: Partial<Annotations>[]) => void;
  annotations: Annotations[];
  plotDiv: PlotlyHTMLElement;
}) {
  if (popupData.text != undefined && popupData.text != "") {
    popupData.text = popupData.text.replace(/\n/g, "<br>");
    let popup_data: Partial<PopupData>;

    if (popupData.annotation) {
      console.log("data", popupData);
      popup_data = {
        x: popupData.annotation.x,
        y: popupData.annotation.y,
        yref: popupData.annotation.yref,
        yanchor:
          popupData.annotation.y < popupData.annotation.ay ? "above" : "below",
        ...popupData,
      };
      console.log("popup_data", popup_data);
      let to_update = plot_text({
        plotData,
        popup_data: popup_data as PopupData,
        current_text: popupData.annotation.text,
      });
      setAnnotations(
        [...annotations, to_update.annotation].filter((a) => a != undefined)
      );
      plotData.layout.dragmode = "pan";
      setPlotData({ ...plotData, ...to_update.update });
      setOnAnnotationClick({});

      return;
    }

    plotDiv.on("plotly_clickannotation", (eventData) => {
      console.log("plotly_clickannotation", eventData);
      let annotation = eventData.annotation;

      if (annotation.text == undefined) {
        console.log("annotation.text is undefined");
        return;
      }
      console.log("annotation.text", annotation.text);
      // we replace <br> with \n so that the textarea can display the text properly
      annotation.text = annotation.text.replace(/<br>/g, "\n");

      let popup_data = {
        x: annotation.x,
        y: annotation.y,
        yanchor: annotation.y < annotation.ay ? "above" : "below",
        text: annotation.text,
        color: annotation.font.color,
        size: annotation.font.size,
        bordercolor: annotation.bordercolor,
        annotation: annotation,
      };
      console.log("popup_data", popup_data);
      setOnAnnotationClick(popup_data);
      setModal({ name: "textDialog", data: popup_data });
      setOnAnnotationClick({});
    });

    function clickHandler(eventData: PlotMouseEvent) {
      console.log("plotly_click", eventData);
      let x = eventData.points[0].x;
      let yaxis = eventData.points[0].fullData.yaxis;
      let y = 0;

      // We need to check if the trace is a candlestick or not
      // this is because the y value is stored in the high or low
      if (eventData.points[0].y != undefined) {
        y = eventData.points[0].y;
      } else if (eventData.points[0].low != undefined) {
        if (popup_data?.yanchor == "below") {
          y = eventData.points[0].low;
        } else {
          y = eventData.points[0].high;
        }
      }

      popup_data = {
        x: onAnnotationClick?.annotation?.x ?? x,
        y: onAnnotationClick?.annotation?.y ?? y,
        yref: onAnnotationClick?.annotation?.yref ?? yaxis,
        ...popupData,
      };
      let to_update = plot_text({
        plotData,
        popup_data: popup_data as PopupData,
        current_text: onAnnotationClick?.annotation?.text,
      });
      setAnnotations(
        [...annotations, to_update.annotation].filter((a) => a != undefined)
      );
      plotData.layout.dragmode = "pan";
      setPlotData({ ...plotData, ...to_update.update });

      plotDiv.removeAllListeners("plotly_click");
    }
    plotData.layout.dragmode = "select";
    setPlotData({ ...plotData });
    plotDiv.on("plotly_click", clickHandler);
  }
}
