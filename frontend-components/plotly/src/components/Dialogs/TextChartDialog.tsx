import CommonDialog from "./CommonDialog";
import { useState } from "react";

const style = {
  padding: "5px 2px 2px 5px",
  margin: "2px 0",
};

export default function TextChartDialog({
  open,
  close,
  addAnnotation,
  deleteAnnotation,
  popupData,
}: {
  plotlyData: any;
  open: boolean;
  close: () => void;
  addAnnotation: (annotation: any) => void;
  updateAnnotation: (annotation: any) => void;
  deleteAnnotation: (annotation: any) => void;
  popupData: any | null;
}) {
  const defaultPopupData = {
    text: "",
    color: "#0088CC",
    size: 18,
    bordercolor: "#822661",
    yanchor: "above",
  };
  const [popUpData, setPopUpData] = useState<any>(defaultPopupData);
  const [newPopupData, setNewPopupData] = useState<any>(defaultPopupData);

  if (popupData && popupData !== popUpData) {
    if (popupData.annotation) {
      popupData.annotation = popupData?.annotation || {};
      setPopUpData(popupData);
      setNewPopupData(popupData);
    }
  }

  function onClose() {
    console.log("closing");
    setPopUpData(defaultPopupData);
    setNewPopupData(defaultPopupData);
    close();
  }

  function onChange(e: any) {
    console.log(e.target.id.replace("addtext_", ""), e.target.value);
    const name = e.target.id.replace("addtext_", "");
    const value =
      e.target.type === "checkbox"
        ? e.target.checked
          ? 1
          : 0
        : e.target.value;
    setNewPopupData({ ...newPopupData, [name]: value });
  }

  function onSubmit() {
    console.log("submitting", newPopupData);
    if (newPopupData.text !== "") {
      let above = ["above", 1].includes(newPopupData.yanchor);
      newPopupData.yanchor = above ? "above" : "below";

      if (popUpData?.annotation) {
        setNewPopupData({ ...newPopupData, annotation: popUpData.annotation });
      }
      addAnnotation(newPopupData);
      close();
    } else {
      document.getElementById("popup_textarea_warning")!.style.display =
        "block";
      document.getElementById("addtext_text")!.style.border = "1px solid red";
    }
  }
  function onDelete() {
    deleteAnnotation(popUpData);
    onClose();
  }

  return (
    <CommonDialog
      title="Add Text to Chart"
      description="Change the titles on the chart."
      open={open}
      close={onClose}
    >
      <div id="popup_title" className="popup_content">
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          <div style={{ marginBottom: 20 }}>
            <label htmlFor="popup_text">
              <b>Text:</b>
              <div id="popup_textarea_warning" className="popup_warning">
                Text is required
              </div>
            </label>
            <textarea
              id="addtext_text"
              style={{
                ...style,
                width: "100%",
                maxWidth: "100%",
                maxHeight: "200px",
                marginTop: "8px",
              }}
              rows={4}
              cols={50}
              placeholder="Enter text here"
              onChange={onChange}
              defaultValue={popUpData?.annotation?.text || newPopupData?.text}
            ></textarea>
          </div>
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <div>
              <label htmlFor="addtext_color">
                <b>Font color:</b>
              </label>
              <input
                type="color"
                id="addtext_color"
                defaultValue={
                  popUpData?.annotation?.color || newPopupData?.color
                }
                onChange={onChange}
              ></input>
            </div>
            <div>
              <label htmlFor="addtext_bordercolor">
                <b>Border color:</b>
              </label>
              <input
                type="color"
                id="addtext_bordercolor"
                defaultValue={
                  popUpData?.annotation?.bordercolor ||
                  newPopupData?.bordercolor
                }
                onChange={onChange}
              ></input>
            </div>
          </div>

          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <div>
              <label htmlFor="addtext_size">
                <b>Font size:</b>
              </label>
              <input
                style={{ ...style, width: "45px" }}
                type="number"
                id="addtext_size"
                onChange={onChange}
                defaultValue={popUpData?.annotation?.size || newPopupData?.size}
              ></input>
            </div>
            <div>
              <label htmlFor="addtext_yanchor">
                <b>Position (Above):</b>
              </label>
              <input
                type="checkbox"
                id="addtext_yanchor"
                name="check"
                defaultChecked={
                  newPopupData?.yanchor === "above" ? true : false
                }
                onChange={onChange}
              ></input>
            </div>
          </div>
        </div>

        <div style={{ float: "right", marginTop: 20 }}>
          <button
            className="_btn-tertiary ph-capture"
            id="title_cancel"
            onClick={onClose}
          >
            Cancel
          </button>
          <button
            className="_btn ph-capture"
            id="title_delete"
            onClick={onDelete}
          >
            Delete
          </button>
          <button
            className="_btn ph-capture"
            id="title_submit"
            onClick={onSubmit}
          >
            Submit
          </button>
        </div>
      </div>
    </CommonDialog>
  );
}
