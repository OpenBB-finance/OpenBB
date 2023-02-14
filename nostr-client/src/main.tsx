import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";
import { NostrProvider } from "nostr-react";

const relayUrls = ["ws://192.168.1.168:6969"];

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <NostrProvider relayUrls={relayUrls} debug={true}>
      <App />
    </NostrProvider>
  </React.StrictMode>
);
