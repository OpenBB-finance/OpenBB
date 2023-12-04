import { useLocation } from "@docusaurus/router";
import DocSidebarItemCategory from "@theme/DocSidebarItem/Category";
import DocSidebarItemHtml from "@theme/DocSidebarItem/Html";
import DocSidebarItemLink from "@theme/DocSidebarItem/Link";
import React from "react";
import { useIFrameContext } from "../Root";

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
  const isPro = pathname.startsWith("/pro");
  const isExcel = pathname.startsWith("/excel");

  // Check if the item is the OpenBB Terminal Pro section
  if (item.customProps?.hiddenByDefault && !(isPro || isExcel)) {
    return null;
  }

  if (isIFrame) {
    const firstTwoPathSegments = pathname.split("/").slice(0, 3).join("/");

    if (shouldHideItem(item, firstTwoPathSegments)) {
      return null;
    }
  }

  if ((isPro || isExcel) && !checkIfAnyChildIsProExcel(item)) {
    return null;
  } else if (!(isPro || isExcel) && item.href?.startsWith("/pro") && item.href?.startsWith("/excel")) {
    return null;
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

function checkIfAnyChildIsProExcel(item) {
  if (item.items) {
    return item.items.some((childItem) => checkIfAnyChildIsProExcel(childItem));
  }

  if (item.type === "link") {
    return item.href?.startsWith("/pro") || item.href?.startsWith("/excel");
  }

  if (item.type === "category") {
    return item.items.some((childItem) => checkIfAnyChildIsProExcel(childItem));
  }

  return false;
}
