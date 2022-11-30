import React from "react";
import clsx from "clsx";
import TOCItems from "@theme/TOCItems";
import styles from "./styles.module.css";
import { useLocation } from "@docusaurus/router";
// Using a custom className
// This prevents TOCInline/TOCCollapsible getting highlighted by mistake
const LINK_CLASS_NAME = "table-of-contents__link toc-highlight";
const LINK_ACTIVE_CLASS_NAME = "table-of-contents__link--active";
export default function TOC({ className, ...props }) {
  const { pathname } = useLocation()
  if (pathname.startsWith("/sdk/reference/")) return null
  return (
    <div
      className={clsx(
        styles.tableOfContents,
        "thin-scrollbar text-sm mt-[48px] xl:max-w-[216px]",
        className
      )}
    >
      <p className="uppercase text-sm font-bold text-grey-600 dark:text-grey-200 tracking-widest mb-2">
        On this page
      </p>
      <TOCItems
        {...props}
        linkClassName={
          "text-grey-400 capitalize !no-underline"
        }
        linkActiveClassName={"!text-white"}
      />
    </div>
  );
}
