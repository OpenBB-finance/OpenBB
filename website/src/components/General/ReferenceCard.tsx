import Link from "@docusaurus/Link";
import clsx from "clsx";
import React from "react";

import { useLocation } from "@docusaurus/router";

export default function ReferenceCard({
  title,
  url,
  description,
  command,
}: {
  title: string;
  url: string;
  description: string;
  command: string;
}) {
  // TODO: Waiting for mockup of how to display the command vs menu item
  const something = command ? "" : "";
  const { pathname } = useLocation();
  const cleanedPath = pathname.replace(/\/v\d+/, "");
  return (
    <Link
      className={clsx(
        "rounded border-2 !no-underline border-grey-600 p-6 cursor-pointer relative overflow-hidden hover:shadow-2xl hover:-translate-y-2 transform transition-all duration-300 ease-in-out font-bold shadow-2xl",
        {
          header_docs_terminal: cleanedPath.startsWith("/terminal"),
          "bg-gradient-to-r from-[#541c12] to-[rgba(84, 29, 19, 1)]":
            cleanedPath.startsWith("/sdk") ||
            cleanedPath.startsWith("/platform"),
          "bg-gradient-to-r from-grey-800 to-purple-800":
            cleanedPath.startsWith("/bot"),
          header_docs:
            !cleanedPath.startsWith("/terminal") &&
            !cleanedPath.startsWith("/sdk") &&
            !cleanedPath.startsWith("/platform") &&
            !cleanedPath.startsWith("/bot"),
        },
      )}
      to={url}
    >
      <div className="absolute top-0 right-0 left-0 bottom-0 bg-gradient-to-t from-black to-transparent" />
      <p className={"py-2 font-bold text-lg my-0"}>
        {title}
        {something}
      </p>
      {description ? (
        <p className="text-grey-200 text-xs mt-2 mb-0">{description}</p>
      ) : null}
    </Link>
  );
}
