import CommonDialog from "./CommonDialog";
import { useState, useEffect, useRef } from "react";

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
  updateAnnotation?: (annotation: any) => void;
  deleteAnnotation: (annotation: any) => void;
  popupData: any | null;
}) {
  // Prevent multiple renderings
  const hasLoaded = useRef(false);

  const defaultPopupData = {
    text: "",
    color: "#0088CC",
    size: 18,
    bordercolor: "#822661",
    arrowcolor: "#822661",
    bgcolor: "#000000",
    arrowsize: 1,
    arrowwidth: 2,
    yanchor: "above",
  };

  // Use a single state object to hold all form data
  const [formData, setFormData] = useState<any>(defaultPopupData);
  const [editMode, setEditMode] = useState(false);

  // Handle initialization when dialog opens
  useEffect(() => {
    if (open && popupData?.annotation && !hasLoaded.current) {
      const annotation = popupData.annotation;

      // Get properties from annotation for editing
      let data = {
        text: annotation.text || "",
        color: annotation.font?.color || defaultPopupData.color,
        size: annotation.font?.size || defaultPopupData.size,
        bordercolor: annotation.bordercolor || defaultPopupData.bordercolor,
        bgcolor: annotation.bgcolor || defaultPopupData.bgcolor,
        arrowcolor: annotation.arrowcolor || defaultPopupData.arrowcolor,
        arrowsize: annotation.arrowsize || defaultPopupData.arrowsize,
        arrowwidth: annotation.arrowwidth || defaultPopupData.arrowwidth,
        yanchor: "above",
      };

      // Determine position based on annotation coordinates
      if (annotation.y !== undefined && annotation.ay !== undefined) {
        data.yanchor = annotation.y < annotation.ay ? "above" : "below";
      }

      setFormData(data);
      setEditMode(true);
      hasLoaded.current = true;
    } else if (!open) {
      // Reset when dialog closes
      setFormData(defaultPopupData);
      setEditMode(false);
      hasLoaded.current = false;
    } else if (open && !popupData?.annotation) {
      // Reset for new annotations
      setFormData(defaultPopupData);
      setEditMode(false);
    }
  }, [open, popupData]);

  function onChange(e: any) {
    const name = e.target.id.replace("addtext_", "");
    let value = e.target.value;

    // Convert numeric values
    if (name === "size" || name === "arrowsize" || name === "arrowwidth") {
      value = parseFloat(value);
    }

    setFormData((prev: any) => ({
      ...prev,
      [name]: value
    }));
  }

  function onClose() {
    close();
  }

  function onSubmit() {
    if (formData.text) {
      const dataToSubmit = { ...formData };

      // Add the annotation reference for editing
      if (editMode && popupData?.annotation) {
        dataToSubmit.annotation = popupData.annotation;
      }

      addAnnotation(dataToSubmit);
      close();
    } else {
      if (document.getElementById("popup_textarea_warning")) {
        document.getElementById("popup_textarea_warning")!.style.display = "block";
      }
      if (document.getElementById("addtext_text")) {
        document.getElementById("addtext_text")!.style.border = "1px solid red";
      }
    }
  }

  function onDelete() {
    if (editMode && popupData) {
      deleteAnnotation(popupData);
    }
    close();
  }

  return (
    <CommonDialog
      title={editMode ? "Edit Annotation" : "Add Text to Chart"}
      description="Add or edit text annotations on the chart."
      open={open}
      close={onClose}
    >
      <div id="popup_title" className="popup_content">
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          <div style={{ marginBottom: 20 }}>
            <label htmlFor="popup_text">
              <b>Text:</b>
              <div id="popup_textarea_warning" className="popup_warning" style={{display: "none"}}>
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
              value={formData.text || ""}
            ></textarea>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: "12px",
              marginBottom: 20,
            }}
          >
            {/* Row 1 */}
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <label htmlFor="addtext_color">
                <b>Font color</b>
              </label>
              <input
                type="color"
                id="addtext_color"
                style={{ margin: "2px 0" }}
                value={formData.color}
                onChange={onChange}
              />
            </div>

            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <label htmlFor="addtext_size">
                <b>Font size</b>
              </label>
              <input
                style={{ width: "52px" }}
                type="number"
                id="addtext_size"
                value={formData.size}
                onChange={onChange}
              />
            </div>

            {/* Row 2 */}
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <label htmlFor="addtext_bgcolor">
                <b>Background</b>
              </label>
              <input
                type="color"
                id="addtext_bgcolor"
                style={{ margin: "2px 0" }}
                value={formData.bgcolor}
                onChange={onChange}
              />
            </div>

            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <label htmlFor="addtext_bordercolor">
                <b>Border color</b>
              </label>
              <input
                type="color"
                id="addtext_bordercolor"
                style={{ margin: "2px 0" }}
                value={formData.bordercolor}
                onChange={onChange}
              />
            </div>

            {/* Row 3 */}
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <label htmlFor="addtext_arrowcolor">
                <b>Arrow color</b>
              </label>
              <input
                type="color"
                id="addtext_arrowcolor"
                style={{ margin: "2px 0" }}
                value={formData.arrowcolor}
                onChange={onChange}
              />
            </div>

            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <label htmlFor="addtext_arrowsize">
                <b>Arrow size</b>
              </label>
              <input
                style={{ width: "52px" }}
                type="number"
                id="addtext_arrowsize"
                min="0.1"
                max="5"
                step="0.1"
                value={formData.arrowsize}
                onChange={onChange}
              />
            </div>

            {/* Row 4 */}
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <label htmlFor="addtext_arrowwidth">
                <b>Arrow width</b>
              </label>
              <input
                style={{ width: "52px" }}
                type="number"
                id="addtext_arrowwidth"
                min="1"
                max="10"
                value={formData.arrowwidth}
                onChange={onChange}
              />
            </div>

            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <label htmlFor="addtext_yanchor">
                <b>Position</b>
              </label>
              <select
                id="addtext_yanchor"
                name="yanchor"
                style={{ width: "100px" }}
                value={formData.yanchor}
                onChange={onChange}
              >
                <option value="above">Above</option>
                <option value="below">Below</option>
              </select>
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
          {editMode && (
            <button
              className="_btn ph-capture"
              id="title_delete"
              onClick={onDelete}
            >
              Delete
            </button>
          )}
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
