import React from "react";
import EditThisPage from "@theme-original/EditThisPage";
import { useLocation } from "@docusaurus/router";

export default function EditThisPageWrapper(props) {
  const { pathname } = useLocation();
  if (
    pathname.startsWith("/terminal/reference") ||
    pathname.startsWith("/sdk/reference") ||
    pathname.startsWith("/bot/reference")
  )
    return null;
  return (
    <>
      <EditThisPage {...props} />
    </>
  );
}
