import React from "react";
import DocSidebarItemCategory from "@theme/DocSidebarItem/Category";
import DocSidebarItemLink from "@theme/DocSidebarItem/Link";
import DocSidebarItemHtml from "@theme/DocSidebarItem/Html";
import { useIFrameContext } from "../Root";
import { useLocation } from "@docusaurus/router";

function shouldHideItem(item, productPath) {
  const { href, items } = item;
  if (!href) {
    return items.some((item) => shouldHideItem(item, productPath));
  }
  return !href.startsWith(productPath);
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
