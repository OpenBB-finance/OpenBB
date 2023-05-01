import React from "react";
import ReactDOM from "react-dom";
import App from "./App";
import "./index.css";

declare global {
  interface Window {
    plotly_figure: any;
    export_image: string;
    save_image: boolean;
    title: string;
    Plotly: any;
    MODEBAR: HTMLElement;
  }
}

ReactDOM.render(
  <React.StrictMode>
      <App />
  </React.StrictMode>,
  document.getElementById("root") as HTMLElement
);
