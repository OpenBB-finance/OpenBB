import { useLocation } from "@docusaurus/router";
import posthog from "posthog-js";
import React, { createContext, useContext, useEffect, useState } from "react";

export const iFrameContext = createContext({
  isIFrame: false,
});

export const useIFrameContext = () => useContext(iFrameContext);

export default function Root({ children }) {
  const [isIFrame, setIsIFrame] = useState(false);
  const [posthogLoaded, setPosthogLoaded] = useState(false);
  const location = useLocation();
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
        posthog.onFeatureFlags(() => {
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

  useEffect(() => {
    if (posthogLoaded)
      posthog.capture("$pageview");
  }, [location.pathname, posthogLoaded]);


  useEffect(() => {
    if (location.pathname.startsWith("/pro") || location.pathname.startsWith("/excel")) {
      const cookie = document.cookie?.split(";").find((c) => c.trim().startsWith("docs-login="));
      const payload = decodeURIComponent(cookie?.split('=')[1].split('.')[0]);
      if (isValidBase64(payload)) {
        const decodedPayload = atob(decodeURIComponent(payload));
        // decide what we want to do whether the user is logged in or not
      } else {
        console.error('Invalid base64 string:', payload);
      }
    }
  }, [location.pathname])

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

function isValidBase64(str) {
  try {
    return btoa(atob(str)) == str;
  } catch (err) {
    return false;
  }
}
