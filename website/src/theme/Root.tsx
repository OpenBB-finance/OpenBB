import Head from "@docusaurus/Head";
import React from "react";

export default function Root({ children }) {
  return <>
    <Head>
      <script defer src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{"token": "100eb319cb954b9ea86aa757652c0958"}'></script>
    </Head>
    {children}</>;
}
