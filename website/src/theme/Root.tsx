import React, { createContext, useContext, useEffect, useState } from "react";
import posthog from "posthog-js";
import { useLocation } from "@docusaurus/router";

export const iFrameContext = createContext({
  isIFrame: false,
});

export const useIFrameContext = () => useContext(iFrameContext);

posthog.init("phc_EqU3YjnV8OYmBlKanwWq222B8OHQksfmQBUtcVeteHR", {
  api_host: "https://app.posthog.com",
  autocapture: {
    css_selector_allowlist: [".ph-capture"],
  },
});

export default function Root({ children }) {
  const [isIFrame, setIsIFrame] = useState(false);
  useEffect(() => {
    setIsIFrame(window.self !== window.top);
    if (window.self !== window.top) {
      document.addEventListener("keydown", (e) => {
        if ((e.metaKey || e.ctrlKey) && e.key === "k") {
          e.preventDefault();
          e.stopPropagation();
        }
      });
    }
  }, []);

  const location = useLocation();

  useEffect(() => {
    posthog.capture("$pageview");
  }, [location]);

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
