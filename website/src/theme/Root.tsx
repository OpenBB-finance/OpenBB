import React, { createContext, useContext, useEffect, useState } from "react";
import posthog from "posthog-js";
import { useLocation } from "@docusaurus/router";

export const iFrameContext = createContext({
  isIFrame: false,
});

export const useIFrameContext = () => useContext(iFrameContext);

export default function Root({ children }) {
  const [isIFrame, setIsIFrame] = useState(false);
  const [posthogLoaded, setPosthogLoaded] = useState(false);
  useEffect(() => {
    setIsIFrame(window?.self !== window?.top);
    if (window?.self !== window?.top) {
      document.addEventListener("keydown", (e) => {
        if ((e.metaKey || e.ctrlKey) && e.key === "k") {
          e.preventDefault();
          e.stopPropagation();
        }
      });
    }
    posthog.init("phc_EqU3YjnV8OYmBlKanwWq222B8OHQksfmQBUtcVeteHR", {
      api_host: "https://app.posthog.com",
      autocapture: {
        css_selector_allowlist: [".ph-capture"],
      },
      loaded: () => {
        setPosthogLoaded(true);
        posthog.onFeatureFlags(function () {
          if (!posthog.isFeatureEnabled("record-web", { send_event: false })) {
            posthog.stopSessionRecording();
            console.log("Stopped session recording");
          }
          if (!posthog.isFeatureEnabled("collect-logs-web", { send_event: false })) {
            posthog.opt_out_capturing();
            console.log("Opted out of capturing");
          } else if (posthog.has_opted_out_capturing()) {
            posthog.opt_in_capturing();
            console.log("Opted in to capturing");
          }
        });
      },
    });
  }, []);

  const location = useLocation();

  useEffect(() => {
    if (posthogLoaded)
      posthog.capture("$pageview");
  }, [location.pathname, posthogLoaded]);

  return (
    <iFrameContext.Provider
      value={{
        isIFrame,
      }}
    >
      {children}
    </iFrameContext.Provider>
  );
}
