import Head from "@docusaurus/Head";
import React, { createContext, useContext, useEffect, useState } from "react";

export const iFrameContext = createContext({
  isIFrame: false,
});

export const useIFrameContext = () => useContext(iFrameContext);

export default function Root({ children }) {
  const [isIFrame, setIsIFrame] = useState(false);
  useEffect(() => {
    setIsIFrame(window.self !== window.top);
  }, []);
  return (
    <iFrameContext.Provider
      value={{
        isIFrame,
      }}
    >
      <Head>
        <script
          defer
          src="https://static.cloudflareinsights.com/beacon.min.js"
          data-cf-beacon='{"token": "100eb319cb954b9ea86aa757652c0958"}'
        ></script>
      </Head>
      {children}
    </iFrameContext.Provider>
  );
}
