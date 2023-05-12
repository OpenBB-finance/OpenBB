import CommonDialog, { styleDialog } from "../Dialogs/CommonDialog";
import { useState } from "react";

export default function TitleChartDialog({
  plotlyData,
  open,
  close,
  defaultTitle,
  updateTitle,
  updateAxesTitles,
}: {
  plotlyData?: any;
  open: boolean;
  close: () => void;
  defaultTitle: string;
  updateTitle: (title: string) => void;
  updateAxesTitles: (axesTitles: any) => void;
}) {
  const [title, setTitle] = useState(defaultTitle);

  const yAxes = Object.keys(plotlyData.layout || {}).filter(
    (k) => k.startsWith("yaxis") && plotlyData.layout[k].range != undefined
  );
  const xAxes = Object.keys(plotlyData.layout || {}).filter(
    (k) =>
      k.startsWith("xaxis") &&
      plotlyData.layout[k].showticklabels != undefined &&
      plotlyData.layout[k]?.anchor
  );

  const [axesTitles, setAxesTitles] = useState<any>({});

  return (
    <CommonDialog
      title="Chart Titles"
      description="Change the titles on the chart."
      open={open}
      close={close}
    >
      <div id="popup_title" className="popup_content">
        <div style={{ display: "flex", flexDirection: "column", gap: 0 }}>
          <div>
            <label htmlFor="title_text">
              <b>Title:</b>
            </label>
            <textarea
              id="title_text"
              style={{
                ...styleDialog,
                width: "100%",
                maxWidth: "100%",
                maxHeight: "200px",
                marginTop: "8px",
                marginLeft: "0px",
              }}
              rows={2}
              cols={20}
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            ></textarea>
          </div>
          <div
            id="xaxis_div"
            className="csv_column_container"
            style={{ marginTop: 5, marginBottom: -5 }}
          >
            {xAxes.map((x, i) => (
              <div key={x} style={{ marginTop: 5, marginBottom: 5 }}>
                <label htmlFor={`title_${x}`}>
                  {i === 0 ? <b>X axis:</b> : <b>X axis {i + 1}:</b>}
                </label>
                <input
                  id={`title_${x}`}
                  style={{ marginLeft: "0px", padding: "5px 2px 2px 5px" }}
                  type="text"
                  defaultValue={plotlyData?.layout[x]?.title?.text || ""}
                  onChange={(e) => {
                    setAxesTitles({
                      ...axesTitles,
                      [x]: e.target.value,
                    });
                  }}
                />
              </div>
            ))}
          </div>
          <div
            id="yaxis_div"
            className="csv_column_container"
            style={{ marginTop: 5, marginBottom: 5 }}
          >
            {yAxes.map((y, i) => (
              <div key={y} style={{ marginTop: 10 }}>
                <label htmlFor={`title_${y}`}>
                  {i === 0 ? <b>Y axis:</b> : <b>Y axis {i + 1}:</b>}
                </label>
                <input
                  id={`title_${y}`}
                  style={{ marginLeft: "0px", padding: "5px 2px 2px 5px" }}
                  type="text"
                  defaultValue={plotlyData?.layout[y]?.title?.text || ""}
                  onChange={(e) => {
                    setAxesTitles({
                      ...axesTitles,
                      [y]: e.target.value,
                    });
                  }}
                />
              </div>
            ))}
          </div>
        </div>

        <div style={{ float: "right", marginTop: 20 }}>
          <button
            className="_btn-tertiary ph-capture"
            id="title_cancel"
            onClick={close}
          >
            Cancel
          </button>
          <button
            className="_btn ph-capture"
            id="title_submit"
            onClick={() => {
              updateTitle(title);
              updateAxesTitles(axesTitles);
              close();
            }}
          >
            Submit
          </button>
        </div>
      </div>
    </CommonDialog>
  );
}
