import React, { useState } from "react";
import DocSidebarItemCategory from "@theme/DocSidebarItem/Category";
import DocSidebarItemLink from "@theme/DocSidebarItem/Link";
import DocSidebarItemHtml from "@theme/DocSidebarItem/Html";
import { useIFrameContext } from "../Root";
import { useLocation } from "@docusaurus/router";
import clsx from "clsx";

function shouldHideItem(item, productPath) {
  if (item.items) {
    return item.items.every((childItem) =>
      shouldHideItem(childItem, productPath)
    );
  }

  if (item.type === "link") {
    const itemPath = item.href.replace(/\/$/, "");
    return !itemPath.startsWith(productPath);
  }

  if (item.type === "category") {
    return item.items.every((childItem) =>
      shouldHideItem(childItem, productPath)
    );
  }

  return false;
}

export default function DocSidebarItem({ item, ...props }) {
  const { isIFrame } = useIFrameContext();
  const { pathname } = useLocation();

  if (isIFrame) {
    const firstTwoPathSegments = pathname.split("/").slice(0, 3).join("/");

    if (shouldHideItem(item, firstTwoPathSegments)) {
      return null;
    }
  }

  switch (item.type) {
    case "category":
      return <DocSidebarItemCategory item={item} {...props} />;
    case "html":
      return <DocSidebarItemHtml item={item} {...props} />;
    case "link":
    default:
      return <DocSidebarItemLink item={item} {...props} />;
  }
}
